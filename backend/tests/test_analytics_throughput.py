from datetime import UTC, date, datetime, timedelta, timezone

from analytics.lifecycle import Event
from analytics.throughput import ThroughputRow, compute_throughput

T0 = datetime(2030, 1, 1, tzinfo=UTC)


def ev(kind, hours, to_status=None, request_id=1):
    return Event(request_id, kind, T0 + timedelta(hours=hours), to_status=to_status)


def test_counts_events_per_utc_day_and_omits_other_days():
    rows = compute_throughput(
        [
            ev("request_created", 0),
            ev("request_created", 1, request_id=2),
            ev("staff_answered", 2),
            ev("status_changed", 3, 2),
            ev("status_changed", 4, 3, request_id=2),
            ev("status_changed", 5, 1),  # not a throughput event
            ev("comment_added", 6),  # not a throughput event
            ev("request_deleted", 50, request_id=3),  # day 3 has no throughput events
            ev("status_changed", 30, 2),
        ]
    )
    assert rows == [
        ThroughputRow(date(2030, 1, 1), 2, 1, 1, 1),
        ThroughputRow(date(2030, 1, 2), 0, 0, 1, 0),
    ]


def test_counts_events_again_after_a_reopen():
    rows = compute_throughput([ev("status_changed", 1, 2), ev("status_changed", 3, 2)])
    assert rows == [ThroughputRow(date(2030, 1, 1), 0, 0, 2, 0)]


def test_day_is_taken_in_utc_whatever_the_offset():
    late = datetime(2030, 1, 1, 22, 0, tzinfo=timezone(timedelta(hours=-3)))  # 01:00 UTC on the 2nd
    rows = compute_throughput([Event(1, "request_created", late)])
    assert [r.day for r in rows] == [date(2030, 1, 2)]


def test_no_events_no_rows():
    assert compute_throughput([]) == []
