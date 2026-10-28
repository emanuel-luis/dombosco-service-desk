import pytest

from core.utils import has_comment_permission
from forms.models import Comment, ParentForm

pytestmark = pytest.mark.django_db

URL = "/api/v1/forms/comment/"
S = ParentForm.StatusChoices


def test_comment_permission_without_staff_answer_does_not_crash(world, make_request):
    form = make_request(world.parent)
    assert has_comment_permission(world.parent, form)
    assert has_comment_permission(world.admin, form)
    assert not has_comment_permission(world.staff, form)
    assert not has_comment_permission(world.other_parent, form)


def post(client, form, text="olá"):
    return client.post(URL, {"parent_form_id": form.pk, "comment": text}, format="json")


def test_comments_are_rejected_while_pending(world, make_request, api):
    form = make_request(world.parent)
    for user in (world.parent, world.admin):
        assert post(api(user), form).status_code == 409
    assert not Comment.objects.exists()


def test_only_parent_assigned_staff_and_admin_can_comment(world, make_request, api):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    for user in (world.parent, world.staff, world.admin):
        response = post(api(user), form)
        assert response.status_code == 201
        assert set(response.json()) == {"id", "user", "comment", "created_at", "updated_at"}
    assert post(api(world.other_staff), form).status_code == 404
    assert post(api(world.other_parent), form).status_code == 404
    assert post(api(world.user), form).status_code == 403
    assert post(api(world.visitor), form).status_code == 403


def test_unassigned_staff_cannot_comment_on_a_pending_request(world, make_request, api):
    form = make_request(world.parent)
    assert post(api(world.staff), form).status_code == 403


def test_list_comments_needs_participation_and_works_without_staff_answer(world, make_request, api):
    pending = make_request(world.parent)
    assert api(world.admin).get(URL, {"id": pending.pk}).json() == []
    assert api(world.staff).get(URL, {"id": pending.pk}).status_code == 403
    assert api(world.other_parent).get(URL, {"id": pending.pk}).status_code == 404
    assert api(world.parent).get(URL, {"id": 9999}).status_code == 404
    assert api(world.parent).get(URL).status_code == 400


def test_comment_requires_text_and_request_id(world, make_request, api):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    client = api(world.parent)
    assert client.post(URL, {"parent_form_id": form.pk}, format="json").status_code == 400
    assert client.post(URL, {"comment": "x"}, format="json").status_code == 400
    assert post(client, form, "").status_code == 400
    assert post(client, type("F", (), {"pk": 9999}), "x").status_code == 404


def test_only_the_author_edits_and_deletes_while_in_progress(world, make_request, api):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    comment_id = post(api(world.parent), form, "antes").json()["id"]

    def put(user, text="depois"):
        return api(user).put(f"{URL}?id={comment_id}", {"comment": text}, format="json")

    for other in (world.staff, world.admin):
        assert put(other).status_code == 403
        assert api(other).delete(f"{URL}?id={comment_id}").status_code == 403
    assert put(world.other_parent).status_code == 404
    assert put(world.parent).json()["comment"] == "depois"
    assert api(world.parent).delete(f"{URL}?id={comment_id}").status_code == 200
    assert not Comment.objects.exists()


@pytest.mark.parametrize("status", [S.FINALIZADO, S.CANCELADO])
def test_comments_are_frozen_once_the_request_closes(world, make_request, api, status):
    form = make_request(world.parent, S.ANDAMENTO, world.staff)
    comment_id = post(api(world.parent), form).json()["id"]
    form.status = status
    form.save()
    client = api(world.parent)
    assert client.put(f"{URL}?id={comment_id}", {"comment": "x"}, format="json").status_code == 409
    assert client.delete(f"{URL}?id={comment_id}").status_code == 409
    assert post(client, form).status_code == 201  # adding stays allowed once answered


def test_unknown_comment_is_404(world, api):
    assert api(world.parent).delete(f"{URL}?id={12345}").status_code == 404
    assert api(world.user).delete(f"{URL}?id={12345}").status_code == 403
