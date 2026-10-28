from datetime import UTC, datetime

import pytest

from forms import services
from forms.exceptions import RequestConflict, RequestForbidden, RequestInvalid, RequestNotFound
from forms.models import ParentForm, StaffForm
from tests.conftest import REQUEST_DATA

pytestmark = pytest.mark.django_db

S = ParentForm.StatusChoices


def test_create_answer_finalize(world):
    form = services.create_request(world.parent, dict(REQUEST_DATA))
    assert form.status == S.PENDENTE
    assert form.responsible_party == world.parent

    answer = services.answer_request(world.staff, form.pk, {"school_advice": "ok"})
    form.refresh_from_db()
    assert form.status == S.ANDAMENTO
    assert answer.assigned_staff == world.staff

    services.change_status(world.staff, form.pk, S.FINALIZADO)
    form.refresh_from_db()
    assert form.status == S.FINALIZADO


def test_pending_request_can_be_cancelled_by_admin_or_assigned_staff_after_answer(
    world, make_request
):
    form = make_request(world.parent)
    with pytest.raises(RequestForbidden):  # not assigned yet
        services.change_status(world.staff, form.pk, S.CANCELADO)
    services.change_status(world.admin, form.pk, S.CANCELADO)
    form.refresh_from_db()
    assert form.status == S.CANCELADO


def test_assigned_staff_cancels_in_progress_request(world, make_request):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    services.change_status(world.staff, form.pk, S.CANCELADO)
    form.refresh_from_db()
    assert form.status == S.CANCELADO


@pytest.mark.parametrize("terminal", [S.FINALIZADO, S.CANCELADO])
@pytest.mark.parametrize("target", list(S))
def test_terminal_states_reject_staff_transitions(world, make_request, terminal, target):
    form = make_request(world.parent, terminal, world.staff)
    with pytest.raises(RequestConflict):
        services.change_status(world.staff, form.pk, target)


@pytest.mark.parametrize("target", [S.PENDENTE, S.ANDAMENTO])
def test_staff_cannot_go_back_or_repeat(world, make_request, target):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    with pytest.raises(RequestConflict):
        services.change_status(world.staff, form.pk, target)


def test_another_staffs_request_is_invisible_to_staff(world, make_request):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    with pytest.raises(RequestNotFound):
        services.change_status(world.other_staff, form.pk, S.FINALIZADO)


def test_admin_can_move_backwards_even_from_terminal(world, make_request):
    form = make_request(world.parent, S.FINALIZADO, world.staff)
    services.change_status(world.admin, form.pk, S.PENDENTE)
    form.refresh_from_db()
    assert form.status == S.PENDENTE


@pytest.mark.parametrize("bad", [7, -1, None, "x", 1.5, True])
def test_invalid_status_is_rejected(world, make_request, bad):
    form = make_request(world.parent)
    with pytest.raises(RequestInvalid):
        services.change_status(world.admin, form.pk, bad)


def test_second_answer_conflicts(world, make_request):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    with pytest.raises(RequestConflict):
        services.answer_request(world.staff, form.pk, {})
    assert StaffForm.objects.filter(parent_form=form).count() == 1


@pytest.mark.parametrize("terminal", [S.CANCELADO, S.FINALIZADO])
def test_answering_a_closed_request_conflicts_and_does_not_reopen(world, make_request, terminal):
    form = make_request(world.parent, terminal, world.staff)
    with pytest.raises(RequestConflict):
        services.answer_request(world.staff, form.pk, {})
    form.refresh_from_db()
    assert form.status == terminal


@pytest.mark.parametrize("terminal", [S.CANCELADO, S.FINALIZADO])
def test_superuser_answering_a_closed_unanswered_request_conflicts(
    world, make_user, make_request, terminal
):
    superuser = make_user("root@example.com", is_superuser=True)
    form = make_request(world.parent)
    services.change_status(world.admin, form.pk, terminal)
    with pytest.raises(RequestConflict):
        services.answer_request(superuser, form.pk, {})
    form.refresh_from_db()
    assert form.status == terminal
    assert not StaffForm.objects.exists()


def test_only_staff_answer_and_only_parents_create(world, make_request):
    form = make_request(world.parent)
    for user in (world.parent, world.user, world.visitor):
        with pytest.raises(RequestForbidden):
            services.answer_request(user, form.pk, {})
    for user in (world.staff, world.user, world.visitor):
        with pytest.raises(RequestForbidden):
            services.create_request(user, dict(REQUEST_DATA))


def test_parent_updates_and_deletes_only_own_pending_request(world, make_request):
    form = make_request(world.parent)
    services.update_request(world.parent, form.pk, {"student_name": "Novo"})
    form.refresh_from_db()
    assert form.student_name == "Novo"
    with pytest.raises(RequestNotFound):
        services.update_request(world.other_parent, form.pk, {"student_name": "X"})
    with pytest.raises(RequestNotFound):
        services.delete_request(world.other_parent, form.pk)
    with pytest.raises(RequestForbidden):
        services.update_request(world.staff, form.pk, {"student_name": "X"})
    services.delete_request(world.parent, form.pk)
    assert not ParentForm.objects.exists()


def test_parent_cannot_change_or_delete_after_pending(world, make_request):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    with pytest.raises(RequestConflict):
        services.update_request(world.parent, form.pk, {"student_name": "X"})
    with pytest.raises(RequestConflict):
        services.delete_request(world.parent, form.pk)


def test_now_is_injectable(world):
    t1 = datetime(2030, 1, 1, 12, tzinfo=UTC)
    t2 = datetime(2030, 1, 2, 12, tzinfo=UTC)
    form = services.create_request(world.parent, dict(REQUEST_DATA), now=lambda: t1)
    form.refresh_from_db()
    assert form.created_at == form.updated_at == t1

    answer = services.answer_request(world.staff, form.pk, {}, now=lambda: t2)
    form.refresh_from_db()
    answer.refresh_from_db()
    assert form.status == S.ANDAMENTO
    assert form.updated_at == answer.created_at == t2
    assert form.created_at == t1
