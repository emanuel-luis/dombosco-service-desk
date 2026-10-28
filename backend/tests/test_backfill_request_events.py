from datetime import UTC, datetime, timedelta

import pytest
from django.core.management import call_command

from forms import services
from forms.models import ParentForm, RequestEvent
from tests.conftest import REQUEST_DATA

pytestmark = pytest.mark.django_db

S = ParentForm.StatusChoices
T0 = datetime(2030, 1, 1, tzinfo=UTC)


def at(hours):
    return lambda: T0 + timedelta(hours=hours)


@pytest.fixture
def legacy(world):
    """Three requests built through the services, then the event log is wiped."""
    done = services.create_request(world.parent, dict(REQUEST_DATA), now=at(0))
    services.answer_request(world.staff, done.pk, {}, now=at(1))
    services.add_comment(world.parent, done.pk, "oi", now=at(2))
    services.change_status(world.staff, done.pk, S.FINALIZADO, now=at(3))
    cancelled = services.create_request(world.parent, dict(REQUEST_DATA), now=at(4))
    services.change_status(world.admin, cancelled.pk, S.CANCELADO, now=at(5))
    open_ = services.create_request(world.parent, dict(REQUEST_DATA), now=at(6))
    RequestEvent._base_manager.all().delete()  # bypasses the append-only guard
    return done, cancelled, open_


def derived():
    rows = RequestEvent.objects.order_by("request_id", "occurred_at", "event_type")
    return [
        (e.request_id, e.event_type, e.from_status, e.to_status, e.occurred_at, e.actor_role)
        for e in rows
    ]


def test_backfill_derives_events_and_is_idempotent(world, legacy):
    done, cancelled, open_ = legacy
    call_command("backfill_request_events")
    first = derived()
    call_command("backfill_request_events")
    assert derived() == first
    assert {e.source for e in RequestEvent.objects.all()} == {"backfill"}

    def h(n):
        return T0 + timedelta(hours=n)

    assert first == sorted(
        [
            (done.pk, "request_created", None, None, h(0), "parent"),
            (done.pk, "staff_answered", None, None, h(1), "staff"),
            (done.pk, "status_changed", 0, 1, h(1), "staff"),
            (done.pk, "comment_added", None, None, h(2), "parent"),
            (done.pk, "status_changed", 1, 2, h(3), "system"),
            (cancelled.pk, "request_created", None, None, h(4), "parent"),
            (cancelled.pk, "status_changed", 0, 3, h(5), "system"),
            (open_.pk, "request_created", None, None, h(6), "parent"),
        ],
        key=lambda r: (r[0], r[4], r[1]),
    )
    assert RequestEvent.objects.filter(comment_id__isnull=False).count() == 1
