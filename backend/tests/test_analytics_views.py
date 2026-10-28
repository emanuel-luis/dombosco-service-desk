"""The analytics views against a log built through the services with an injected clock.

Postgres only: the views do not exist on SQLite. Times are hours after T0 (a UTC midnight):

  r1 created 0, answered 2, finished 30         r4 created 27, deleted 29
  r2 created 1, cancelled 5 (never answered)    r5 created 2, answered 3, finished 8,
  r3 created 26, answered 29, still open           reopened by an admin at 50
"""

import dataclasses
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from analytics.lifecycle import LifecycleRow, compute_lifecycle
from analytics.models import BacklogByStatus, DailyThroughput, RequestLifecycle, SlaSummary
from analytics.throughput import ThroughputRow, compute_throughput
from forms import services
from forms.models import ParentForm, RequestEvent
from tests.conftest import REQUEST_DATA

pytestmark = [pytest.mark.django_db, pytest.mark.postgres]

S = ParentForm.StatusChoices
T0 = datetime(2030, 1, 1, tzinfo=UTC)
D = Decimal


def at(hours):
    return lambda: T0 + timedelta(hours=hours)


def when(hours):
    return T0 + timedelta(hours=hours)


@pytest.fixture
def scenario(world):
    def create(hours):
        return services.create_request(world.parent, dict(REQUEST_DATA), now=at(hours)).pk

    r1 = create(0)
    services.answer_request(world.staff, r1, {}, now=at(2))
    services.change_status(world.staff, r1, S.FINALIZADO, now=at(30))
    r2 = create(1)
    services.change_status(world.admin, r2, S.CANCELADO, now=at(5))
    r3 = create(26)
    services.answer_request(world.staff, r3, {}, now=at(29))
    r4 = create(27)
    services.delete_request(world.parent, r4, now=at(29))
    r5 = create(2)
    services.answer_request(world.staff, r5, {}, now=at(3))
    services.change_status(world.staff, r5, S.FINALIZADO, now=at(8))
    services.change_status(world.admin, r5, S.ANDAMENTO, now=at(50))
    return {"r1": r1, "r2": r2, "r3": r3, "r4": r4, "r5": r5}


def lifecycle_tuples(rows):
    names = [f.name for f in dataclasses.fields(LifecycleRow)]
    return [tuple(getattr(row, name) for name in names) for row in rows]


def test_lifecycle_view_has_one_row_per_request_seen_in_the_log(scenario):
    rows = {row.request_id: row for row in RequestLifecycle.objects.all()}
    assert set(rows) == set(scenario.values())

    r1, r2, r3, r4, r5 = (rows[scenario[k]] for k in ("r1", "r2", "r3", "r4", "r5"))
    assert (r1.opened_at, r1.first_response_at, r1.closed_at) == (when(0), when(2), when(30))
    assert (r1.current_status, r1.hours_to_first_response, r1.hours_to_close) == (
        2,
        D("2.00"),
        D("30.00"),
    )
    assert (r2.current_status, r2.first_response_at, r2.hours_to_first_response) == (3, None, None)
    assert (r2.closed_at, r2.hours_to_close) == (when(5), D("4.00"))
    assert (r3.current_status, r3.closed_at, r3.hours_to_first_response) == (1, None, D("3.00"))
    assert (r4.deleted, r4.current_status, r4.first_response_at) == (True, 0, None)
    assert (r5.current_status, r5.closed_at, r5.hours_to_close) == (1, None, None)
    assert not any(row.deleted for row in (r1, r2, r3, r5))


def test_lifecycle_view_matches_the_python_definition(scenario):
    from_python = compute_lifecycle(RequestEvent.objects.order_by("id"))
    from_view = [
        LifecycleRow(
            **{f.name: getattr(row, f.name) for f in dataclasses.fields(LifecycleRow)},
        )
        for row in RequestLifecycle.objects.order_by("request_id")
    ]
    assert len(from_python) == 5
    assert lifecycle_tuples(from_view) == lifecycle_tuples(from_python)


def test_daily_throughput_counts_per_utc_day(scenario):
    rows = [
        (r.day, r.opened, r.answered, r.finished, r.cancelled)
        for r in DailyThroughput.objects.order_by("day")
    ]
    # The reopening on day 3 is not a throughput event, so that day has no row.
    assert rows == [(date(2030, 1, 1), 3, 2, 1, 1), (date(2030, 1, 2), 2, 1, 1, 0)]


def test_backlog_ignores_deleted_requests(scenario):
    rows = {
        r.current_status: (r.requests, r.oldest_opened_at) for r in BacklogByStatus.objects.all()
    }
    assert rows == {1: (2, when(2)), 2: (1, when(0)), 3: (1, when(1))}


def test_sla_summary_percentiles_skip_deleted_and_missing_values(scenario):
    sla = SlaSummary.objects.get()
    # First responses 1, 2 and 3 hours; closes 4 and 30 hours (r5 was reopened).
    assert (sla.responded_count, sla.first_response_p50_hours) == (3, D("2.00"))
    assert sla.first_response_p90_hours == D("2.80")
    assert (sla.closed_count, sla.close_p50_hours, sla.close_p90_hours) == (
        2,
        D("17.00"),
        D("27.40"),
    )


def test_views_are_empty_on_an_empty_log(db):
    assert not RequestLifecycle.objects.exists()
    assert not DailyThroughput.objects.exists()
    assert not BacklogByStatus.objects.exists()
    sla = SlaSummary.objects.get()
    assert (sla.responded_count, sla.closed_count) == (0, 0)
    assert sla.first_response_p50_hours is None
    assert sla.close_p90_hours is None


def test_daily_throughput_counts_events_including_reopens_and_deleted_requests(world):
    """Throughput counts events: a finish after a reopen counts again and deleted requests count."""
    r = services.create_request(world.parent, dict(REQUEST_DATA), now=at(0)).pk
    services.answer_request(world.staff, r, {}, now=at(1))
    services.change_status(world.staff, r, S.FINALIZADO, now=at(2))
    services.change_status(world.admin, r, S.ANDAMENTO, now=at(3))
    services.change_status(world.admin, r, S.FINALIZADO, now=at(4))
    gone = services.create_request(world.parent, dict(REQUEST_DATA), now=at(5)).pk
    services.delete_request(world.parent, gone, now=at(6))
    rows = [
        (row.day, row.opened, row.answered, row.finished, row.cancelled)
        for row in DailyThroughput.objects.all()
    ]
    assert rows == [(date(2030, 1, 1), 2, 1, 2, 0)]


def test_daily_throughput_view_matches_the_python_definition(scenario):
    from_python = compute_throughput(RequestEvent.objects.order_by("id"))
    from_view = [
        ThroughputRow(r.day, r.opened, r.answered, r.finished, r.cancelled)
        for r in DailyThroughput.objects.order_by("day")
    ]
    assert len(from_python) == 2
    assert from_view == from_python
