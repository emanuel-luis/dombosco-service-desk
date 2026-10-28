"""Idempotent Parquet export of the analytics datasets, one partition per as-of date.

    <out>/as_of=YYYY-MM-DD/{request_events,request_lifecycle,daily_throughput}.parquet + _run.json

The snapshot is every request_event with occurred_at before the end of the as-of day (UTC),
read in (occurred_at, id) order. The lifecycle and throughput come from that snapshot through
the pure-Python definitions, so the export needs no Postgres view. Every dataset must pass its
contract (analytics.contracts) before anything is written. The partition is written to a
temporary directory next to the target and swapped in with os.replace, so a failed run leaves
the previous partition as it was. Running again on unchanged data gives equal tables (the
files differ only in _run.json); the run_id and timestamps live in _run.json alone.
"""

import dataclasses
import json
import os
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from analytics.contracts import SCHEMAS, CheckResult, check_all
from analytics.lifecycle import compute_lifecycle
from analytics.throughput import compute_throughput
from forms.models import RequestEvent

DATASETS = tuple(SCHEMAS)


class ContractViolation(Exception):
    def __init__(self, failures: list[CheckResult]) -> None:
        self.failures = failures
        super().__init__("; ".join(f"{f.name}: {f.detail or 'failed'}" for f in failures))


@dataclass(frozen=True, slots=True)
class Tables:
    request_events: Any
    request_lifecycle: Any
    daily_throughput: Any


def cutoff_for(as_of: date) -> datetime:
    """Exclusive upper bound of the snapshot: midnight UTC after the as-of day."""
    return datetime.combine(as_of + timedelta(days=1), time.min, tzinfo=UTC)


def snapshot(as_of: date) -> list[RequestEvent]:
    # Known limit: the whole snapshot is held in memory; stream by batches if the log outgrows it.
    return list(
        RequestEvent.objects.filter(occurred_at__lt=cutoff_for(as_of)).order_by("occurred_at", "id")
    )


def build_tables(events: list[RequestEvent]) -> Tables:
    def table(name: str, rows: list[dict[str, Any]]) -> Any:
        return pa.Table.from_pylist(rows, schema=SCHEMAS[name])

    return Tables(
        request_events=table(
            "request_events",
            [
                {
                    "event_id": str(e.event_id),
                    "request_id": e.request_id,
                    "event_type": e.event_type,
                    "actor_id": e.actor_id,
                    "actor_role": e.actor_role,
                    "from_status": e.from_status,
                    "to_status": e.to_status,
                    "comment_id": e.comment_id,
                    "occurred_at": e.occurred_at,
                    "source": e.source,
                }
                for e in events
            ],
        ),
        request_lifecycle=table(
            "request_lifecycle", [dataclasses.asdict(r) for r in compute_lifecycle(events)]
        ),
        daily_throughput=table(
            "daily_throughput", [dataclasses.asdict(r) for r in compute_throughput(events)]
        ),
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _swap(tmp: Path, target: Path) -> None:
    """Replace `target` with `tmp`. A failed swap puts the previous partition back."""
    old = target.with_name(f".old-{target.name}-{uuid.uuid4().hex}")
    if target.exists():
        os.replace(target, old)
    try:
        os.replace(tmp, target)
    except BaseException:
        if old.exists():
            os.replace(old, target)
        raise
    # Known limit: two renames, not one atomic swap; a crash between them leaves .old-* behind
    # with the previous data. Switch to a pointer file if readers must never see a gap.
    shutil.rmtree(old, ignore_errors=True)


def export_partition(as_of: date, out: Path) -> dict[str, Any]:
    """Export the as-of partition under `out` and return what was written to _run.json.

    Raises ContractViolation, leaving any existing partition untouched, when a check fails.
    """
    started_at = _now()
    cutoff = cutoff_for(as_of)
    tables = build_tables(snapshot(as_of))
    results = check_all(
        tables.request_events, tables.request_lifecycle, tables.daily_throughput, cutoff
    )
    if failures := [r for r in results if not r.ok]:
        raise ContractViolation(failures)

    target = out / f"as_of={as_of.isoformat()}"
    out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".tmp-{target.name}-", dir=out))
    try:
        for name in DATASETS:
            pq.write_table(getattr(tables, name), tmp / f"{name}.parquet")
        run = {
            "run_id": str(uuid.uuid4()),
            "as_of": as_of.isoformat(),
            "started_at": started_at,
            "finished_at": _now(),
            "row_counts": {name: getattr(tables, name).num_rows for name in DATASETS},
            "contracts": [dataclasses.asdict(r) for r in results],
            "pyarrow_version": pa.__version__,
        }
        (tmp / "_run.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
        _swap(tmp, target)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return run
