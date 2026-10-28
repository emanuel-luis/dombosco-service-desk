"""The portable definition of daily throughput, computed from request events.

Pure Python, no database access. The v_daily_throughput view (migration 0001) implements the
same rules in SQL and a Postgres test keeps the two equal. Per UTC day of occurred_at, it
counts events, not requests (a finish after a reopen counts again, deleted requests count):

- opened: request_created.
- answered: staff_answered.
- finished: status_changed with to_status 2.
- cancelled: status_changed with to_status 3.

Days with none of those events are omitted. Rows are ordered by day.
"""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, date

from analytics.lifecycle import EventLike


@dataclass(frozen=True, slots=True)
class ThroughputRow:
    day: date
    opened: int
    answered: int
    finished: int
    cancelled: int


def _column(event: EventLike) -> str | None:
    kind = event.event_type
    if kind == "request_created":
        return "opened"
    if kind == "staff_answered":
        return "answered"
    if kind == "status_changed" and event.to_status == 2:
        return "finished"
    if kind == "status_changed" and event.to_status == 3:
        return "cancelled"
    return None


def compute_throughput(events: Iterable[EventLike]) -> list[ThroughputRow]:
    """One row per UTC day that has at least one throughput event, ordered by day."""
    counts: dict[date, Counter[str]] = {}
    for event in events:
        column = _column(event)
        if column is not None:
            day = event.occurred_at.astimezone(UTC).date()
            counts.setdefault(day, Counter())[column] += 1
    return [
        ThroughputRow(day, c["opened"], c["answered"], c["finished"], c["cancelled"])
        for day, c in sorted(counts.items())
    ]
