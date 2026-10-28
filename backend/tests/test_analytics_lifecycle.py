from datetime import UTC, datetime, timedelta
from decimal import Decimal

from analytics.lifecycle import Event, compute_lifecycle

T0 = datetime(2030, 1, 1, tzinfo=UTC)


def at(hours):
    return T0 + timedelta(hours=hours)


def ev(request_id, kind, hours, role="system", to_status=None):
    return Event(request_id, kind, at(hours), role, to_status)


def only(events):
    (row,) = compute_lifecycle(events)
    return row


def test_answered_and_finished():
    row = only(
        [
            ev(1, "request_created", 0, "parent"),
            ev(1, "staff_answered", 2, "staff"),
            ev(1, "status_changed", 2, "staff", 1),
            ev(1, "status_changed", 10, "staff", 2),
        ]
    )
    assert (row.opened_at, row.first_response_at, row.closed_at) == (at(0), at(2), at(10))
    assert row.current_status == 2
    assert not row.deleted
    assert (row.hours_to_first_response, row.hours_to_close) == (Decimal("2.00"), Decimal("10.00"))


def test_unanswered_and_cancelled():
    row = only([ev(1, "request_created", 1, "parent"), ev(1, "status_changed", 5, "admin", 3)])
    assert row.first_response_at is None
    assert row.hours_to_first_response is None
    assert (row.current_status, row.closed_at, row.hours_to_close) == (3, at(5), Decimal("4.00"))


def test_reopened_by_admin_is_not_closed():
    row = only(
        [
            ev(1, "request_created", 0, "parent"),
            ev(1, "staff_answered", 1, "staff"),
            ev(1, "status_changed", 1, "staff", 1),
            ev(1, "status_changed", 4, "staff", 2),
            ev(1, "status_changed", 9, "admin", 1),
        ]
    )
    assert row.current_status == 1
    assert row.closed_at is None
    assert row.hours_to_close is None


def test_deleted_request_keeps_its_row():
    row = only([ev(1, "request_created", 0, "parent"), ev(1, "request_deleted", 3, "parent")])
    assert row.deleted
    assert row.current_status == 0


def test_staff_comment_is_the_first_response_when_earlier_than_the_answer():
    row = only(
        [
            ev(1, "request_created", 0, "parent"),
            ev(1, "comment_added", 1, "parent"),  # parents never count as a response
            ev(1, "comment_added", 3, "staff"),
            ev(1, "staff_answered", 5, "staff"),
        ]
    )
    assert row.first_response_at == at(3)
    assert row.hours_to_first_response == Decimal("3.00")


def test_admin_comment_counts_and_parent_only_comments_do_not():
    admin = only([ev(1, "request_created", 0, "parent"), ev(1, "comment_added", 2, "admin")])
    parent = only([ev(1, "request_created", 0, "parent"), ev(1, "comment_added", 2, "parent")])
    assert admin.first_response_at == at(2)
    assert parent.first_response_at is None


def test_rows_are_per_request_ordered_and_input_order_does_not_matter():
    rows = compute_lifecycle(
        [
            ev(2, "request_created", 0, "parent"),
            ev(1, "status_changed", 5, "staff", 2),
            ev(1, "status_changed", 2, "staff", 1),
            ev(1, "request_created", 0, "parent"),
        ]
    )
    assert [r.request_id for r in rows] == [1, 2]
    assert rows[0].current_status == 2


def test_hours_round_half_up():
    created = Event(1, "request_created", T0)
    # 18 s is 0.005 h, exactly on the rounding tie.
    answered = Event(1, "staff_answered", T0 + timedelta(seconds=18), "staff")
    assert only([created, answered]).hours_to_first_response == Decimal("0.01")
