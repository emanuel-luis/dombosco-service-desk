import pytest
from django.db import DatabaseError, connection

from tests.test_request_event_model import make_event

pytestmark = [pytest.mark.django_db, pytest.mark.postgres]


def test_raw_update_is_rejected_by_the_trigger():
    make_event()
    with pytest.raises(DatabaseError, match="append-only"), connection.cursor() as cursor:
        cursor.execute("UPDATE request_events SET actor_role = 'admin'")


def test_raw_delete_is_rejected_by_the_trigger():
    make_event()
    with pytest.raises(DatabaseError, match="append-only"), connection.cursor() as cursor:
        cursor.execute("DELETE FROM request_events")
