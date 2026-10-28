from datetime import UTC, datetime

import pytest

from forms import services
from forms.exceptions import RequestConflict, RequestForbidden
from forms.models import ParentForm, RequestEvent
from tests.conftest import REQUEST_DATA

pytestmark = pytest.mark.django_db

S = ParentForm.StatusChoices
NOW = datetime(2030, 5, 6, 7, 8, 9, tzinfo=UTC)


def now():
    return NOW


def events(request_id=None):
    qs = RequestEvent.objects.order_by("id")
    if request_id is not None:
        qs = qs.filter(request_id=request_id)
    return [(e.event_type, e.from_status, e.to_status, e.actor_id, e.actor_role) for e in qs]


def test_create_update_delete_request(world):
    form = services.create_request(world.parent, dict(REQUEST_DATA), now=now)
    services.update_request(world.parent, form.pk, {"student_name": "Novo"}, now=now)
    services.delete_request(world.parent, form.pk, now=now)
    pid, role = world.parent.pk, "parent"
    assert events(form.pk) == [
        ("request_created", None, None, pid, role),
        ("request_updated", None, None, pid, role),
        ("request_deleted", None, None, pid, role),
    ]
    assert {e.occurred_at for e in RequestEvent.objects.all()} == {NOW}
    assert {e.source for e in RequestEvent.objects.all()} == {"api"}
    assert not ParentForm.objects.exists()  # the log outlives the request


def test_answer_writes_staff_answered_and_status_change(world, make_request):
    form = make_request(world.parent)
    before = RequestEvent.objects.count()
    services.answer_request(world.staff, form.pk, {}, now=now, source="seed")
    new = list(RequestEvent.objects.order_by("id")[before:])
    assert [(e.event_type, e.from_status, e.to_status) for e in new] == [
        ("staff_answered", None, None),
        ("status_changed", 0, 1),
    ]
    assert {(e.actor_id, e.actor_role, e.occurred_at, e.source) for e in new} == {
        (world.staff.pk, "staff", NOW, "seed")
    }


def test_change_status_and_answer_update(world, make_request):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    before = RequestEvent.objects.count()
    answer = form.staffform
    services.update_answer(world.staff, answer.pk, {"school_advice": "x"}, now=now)
    services.change_status(world.admin, form.pk, S.FINALIZADO, now=now)
    new = list(RequestEvent.objects.order_by("id")[before:])
    assert [(e.event_type, e.from_status, e.to_status, e.actor_role) for e in new] == [
        ("staff_answer_updated", None, None, "staff"),
        ("status_changed", 1, 2, "admin"),
    ]
    assert {e.request_id for e in new} == {form.pk}


def test_comment_events(world, make_request):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    before = RequestEvent.objects.count()
    comment = services.add_comment(world.parent, form.pk, "oi", now=now)
    services.edit_comment(world.parent, comment.pk, "oi 2", now=now)
    services.delete_comment(world.parent, comment.pk, now=now)
    new = list(RequestEvent.objects.order_by("id")[before:])
    assert [(e.event_type, e.comment_id, e.request_id) for e in new] == [
        ("comment_added", comment.pk, form.pk),
        ("comment_edited", comment.pk, form.pk),
        ("comment_deleted", comment.pk, form.pk),
    ]
    assert {e.occurred_at for e in new} == {NOW}


def test_failed_calls_write_no_event(world, make_request):
    form = make_request(world.parent)
    before = RequestEvent.objects.count()
    with pytest.raises(RequestConflict):
        services.add_comment(world.parent, form.pk, "x", now=now)  # pending
    with pytest.raises(RequestForbidden):
        services.change_status(world.staff, form.pk, S.CANCELADO, now=now)  # not assigned
    with pytest.raises(RequestForbidden):
        services.create_request(world.staff, dict(REQUEST_DATA), now=now)
    assert RequestEvent.objects.count() == before
