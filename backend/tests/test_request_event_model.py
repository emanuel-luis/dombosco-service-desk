import uuid
from datetime import UTC, datetime

import pytest

from forms.models import EventLogImmutable, RequestEvent

pytestmark = pytest.mark.django_db


def make_event(**extra):
    fields = {
        "event_id": uuid.uuid4(),
        "request_id": 1,
        "event_type": "request_created",
        "actor_role": "parent",
        "occurred_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    return RequestEvent.objects.create(**{**fields, **extra})


def test_new_event_defaults_to_api_source():
    assert make_event().source == "api"


def test_saving_an_existing_row_raises():
    event = make_event()
    event.actor_role = "admin"
    with pytest.raises(EventLogImmutable):
        event.save()


def test_deleting_a_row_raises():
    with pytest.raises(EventLogImmutable):
        make_event().delete()


def test_queryset_update_and_delete_raise():
    make_event()
    with pytest.raises(EventLogImmutable):
        RequestEvent.objects.update(actor_role="admin")
    with pytest.raises(EventLogImmutable):
        RequestEvent.objects.all().delete()
    assert RequestEvent.objects.get().actor_role == "parent"
