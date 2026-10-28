"""Data contracts for the Parquet export: Arrow schemas plus the checks that enforce them.

Three datasets, one per layer the export publishes:

- request_events: the raw snapshot of the append-only log (forms.RequestEvent), without
  recorded_at, which is load time and would make two exports of the same data differ.
- request_lifecycle: analytics.lifecycle.compute_lifecycle over that snapshot.
- daily_throughput: analytics.throughput.compute_throughput over that snapshot.

The schema is the contract: exact column names, order and types. A field with nullable=False
is a key or required column, and the checks fail the export when it holds a null. Checks
return structured results instead of raising, so the export can record them in _run.json.
Needs pyarrow (the `export` extra).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pyarrow as pa
import pyarrow.compute as pc

_TS = pa.timestamp("us", tz="UTC")

REQUEST_EVENTS = pa.schema(
    [
        pa.field("event_id", pa.string(), nullable=False),
        pa.field("request_id", pa.int64(), nullable=False),
        pa.field("event_type", pa.string(), nullable=False),
        pa.field("actor_id", pa.int64()),
        pa.field("actor_role", pa.string(), nullable=False),
        pa.field("from_status", pa.int16()),
        pa.field("to_status", pa.int16()),
        pa.field("comment_id", pa.int64()),
        pa.field("occurred_at", _TS, nullable=False),
        pa.field("source", pa.string(), nullable=False),
    ]
)

REQUEST_LIFECYCLE = pa.schema(
    [
        pa.field("request_id", pa.int64(), nullable=False),
        pa.field("opened_at", _TS),
        pa.field("first_response_at", _TS),
        pa.field("closed_at", _TS),
        pa.field("current_status", pa.int16(), nullable=False),
        pa.field("deleted", pa.bool_(), nullable=False),
        pa.field("hours_to_first_response", pa.decimal128(12, 2)),
        pa.field("hours_to_close", pa.decimal128(12, 2)),
    ]
)

DAILY_THROUGHPUT = pa.schema(
    [
        pa.field("day", pa.date32(), nullable=False),
        pa.field("opened", pa.int32(), nullable=False),
        pa.field("answered", pa.int32(), nullable=False),
        pa.field("finished", pa.int32(), nullable=False),
        pa.field("cancelled", pa.int32(), nullable=False),
    ]
)

SCHEMAS: dict[str, Any] = {
    "request_events": REQUEST_EVENTS,
    "request_lifecycle": REQUEST_LIFECYCLE,
    "daily_throughput": DAILY_THROUGHPUT,
}


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


def _schema_check(dataset: str, table: Any) -> CheckResult:
    expected = [(f.name, str(f.type)) for f in SCHEMAS[dataset]]
    actual = [(f.name, str(f.type)) for f in table.schema]
    if actual == expected:
        return CheckResult(f"{dataset}.schema", True)
    return CheckResult(f"{dataset}.schema", False, f"expected {expected}, got {actual}")


def _non_null_check(dataset: str, table: Any) -> CheckResult:
    bad = []
    for field in SCHEMAS[dataset]:
        if not field.nullable and field.name in table.column_names:
            nulls = table.column(field.name).null_count
            if nulls:
                bad.append(f"{field.name} has {nulls} null(s)")
    return CheckResult(f"{dataset}.non_null_keys", not bad, "; ".join(bad))


def _unique_check(dataset: str, table: Any, column: str) -> CheckResult:
    name = f"{dataset}.unique_{column}"
    if column not in table.column_names:
        return CheckResult(name, False, f"missing column {column}")
    values = table.column(column)
    duplicates = len(values) - len(pc.unique(values))
    return CheckResult(
        name, duplicates == 0, f"{duplicates} duplicate value(s)" if duplicates else ""
    )


def check_request_events(table: Any, cutoff: datetime) -> list[CheckResult]:
    """Contract for the raw snapshot. `cutoff` is exclusive: every occurred_at is before it."""
    results = [
        _schema_check("request_events", table),
        _non_null_check("request_events", table),
        _unique_check("request_events", table, "event_id"),
    ]
    name = "request_events.occurred_before_cutoff"
    if "occurred_at" not in table.column_names:
        return [*results, CheckResult(name, False, "missing column occurred_at")]
    latest = pc.max(table.column("occurred_at")).as_py()
    ok = latest is None or latest < cutoff
    return [*results, CheckResult(name, ok, "" if ok else f"{latest} is not before {cutoff}")]


def check_request_lifecycle(table: Any, events: Any) -> list[CheckResult]:
    """Contract for the lifecycle: one row per request_id seen in the snapshot `events`."""
    results = [
        _schema_check("request_lifecycle", table),
        _non_null_check("request_lifecycle", table),
        _unique_check("request_lifecycle", table, "request_id"),
    ]
    name = "request_lifecycle.row_count_matches_events"
    if "request_id" not in events.column_names:
        return [*results, CheckResult(name, False, "snapshot has no request_id column")]
    expected = len(pc.unique(events.column("request_id")))
    ok = table.num_rows == expected
    detail = "" if ok else f"{table.num_rows} rows for {expected} distinct request_id"
    return [*results, CheckResult(name, ok, detail)]


def check_daily_throughput(table: Any) -> list[CheckResult]:
    return [
        _schema_check("daily_throughput", table),
        _non_null_check("daily_throughput", table),
        _unique_check("daily_throughput", table, "day"),
    ]


def check_all(events: Any, lifecycle: Any, throughput: Any, cutoff: datetime) -> list[CheckResult]:
    return [
        *check_request_events(events, cutoff),
        *check_request_lifecycle(lifecycle, events),
        *check_daily_throughput(throughput),
    ]
