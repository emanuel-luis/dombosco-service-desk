"""The portable definition of a request's lifecycle, computed from its events.

Pure Python, no database access. The v_request_lifecycle view (migration 0001) implements the
same rules in SQL and a Postgres test keeps the two equal. Rules, per request_id:

- opened_at: earliest request_created.
- first_response_at: earliest staff_answered, or comment_added by a staff or admin actor,
  whichever comes first.
- current_status: to_status of the latest status_changed, 0 (PENDENTE) when there is none.
- closed_at: occurred_at of that latest status_changed, only when current_status is
  FINALIZADO (2) or CANCELADO (3), so a request an admin reopened has no closed_at.
- deleted: the log holds a request_deleted.
- hours_to_first_response, hours_to_close: elapsed hours rounded half up to 2 decimals,
  None when either end is missing.

Ties on occurred_at are resolved by input order, so feed events in log order (event id).
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import NamedTuple, Protocol

RESPONDING_ROLES = frozenset({"staff", "admin"})
TERMINAL_STATUSES = frozenset({2, 3})
_MICROSECOND = timedelta(microseconds=1)
_MICROSECONDS_PER_HOUR = Decimal(3_600_000_000)
_CENTS = Decimal("0.01")


class EventLike(Protocol):
    """What the function reads from an event; RequestEvent rows and `Event` both fit."""

    @property
    def request_id(self) -> int: ...
    @property
    def event_type(self) -> str: ...
    @property
    def actor_role(self) -> str: ...
    @property
    def to_status(self) -> int | None: ...
    @property
    def occurred_at(self) -> datetime: ...


class Event(NamedTuple):
    """A plain event, handy for hand-built input (tests, exports)."""

    request_id: int
    event_type: str
    occurred_at: datetime
    actor_role: str = "system"
    to_status: int | None = None


@dataclass(frozen=True, slots=True)
class LifecycleRow:
    request_id: int
    opened_at: datetime | None
    first_response_at: datetime | None
    closed_at: datetime | None
    current_status: int
    deleted: bool
    hours_to_first_response: Decimal | None
    hours_to_close: Decimal | None


def _hours(start: datetime | None, end: datetime | None) -> Decimal | None:
    if start is None or end is None:
        return None
    hours = Decimal((end - start) // _MICROSECOND) / _MICROSECONDS_PER_HOUR
    return hours.quantize(_CENTS, rounding=ROUND_HALF_UP)


@dataclass(slots=True)
class _Acc:
    opened_at: datetime | None = None
    first_response_at: datetime | None = None
    last_status: tuple[datetime, int] | None = None
    deleted: bool = False


def compute_lifecycle(events: Iterable[EventLike]) -> list[LifecycleRow]:
    """One row per request_id seen in `events`, ordered by request_id."""
    accs: dict[int, _Acc] = {}
    for event in sorted(events, key=lambda e: e.occurred_at):
        acc = accs.setdefault(event.request_id, _Acc())
        kind = event.event_type
        if kind == "request_created":
            acc.opened_at = acc.opened_at or event.occurred_at
        elif kind == "staff_answered" or (
            kind == "comment_added" and event.actor_role in RESPONDING_ROLES
        ):
            acc.first_response_at = acc.first_response_at or event.occurred_at
        elif kind == "status_changed":
            acc.last_status = (event.occurred_at, event.to_status or 0)
        elif kind == "request_deleted":
            acc.deleted = True

    rows = []
    for request_id in sorted(accs):
        acc = accs[request_id]
        status_at, status = acc.last_status or (None, 0)
        closed_at = status_at if status in TERMINAL_STATUSES else None
        rows.append(
            LifecycleRow(
                request_id=request_id,
                opened_at=acc.opened_at,
                first_response_at=acc.first_response_at,
                closed_at=closed_at,
                current_status=status,
                deleted=acc.deleted,
                hours_to_first_response=_hours(acc.opened_at, acc.first_response_at),
                hours_to_close=_hours(acc.opened_at, closed_at),
            )
        )
    return rows
