import pytest

from forms.models import ParentForm
from tests.conftest import REQUEST_DATA

pytestmark = pytest.mark.django_db

URL = "/api/v1/forms/parent/"
S = ParentForm.StatusChoices


def ids(response):
    return {item["id"] for item in response.json()}


def test_parent_cannot_read_another_parents_request_by_id(world, make_request, api):
    mine = make_request(world.parent)
    theirs = make_request(world.other_parent)
    client = api(world.parent)

    assert client.get(URL, {"id": mine.pk}).status_code == 200
    assert client.get(URL, {"id": theirs.pk}).status_code == 404
    assert ids(client.get(URL)) == {mine.pk}


def test_parent_cannot_update_or_delete_another_parents_request(world, make_request, api):
    theirs = make_request(world.other_parent)
    client = api(world.parent)
    assert client.delete(f"{URL}?id={theirs.pk}").status_code == 404
    assert client.put(URL + f"?id={theirs.pk}", REQUEST_DATA, format="json").status_code == 404
    assert ParentForm.objects.filter(pk=theirs.pk).exists()


def test_staff_sees_pending_and_own_but_not_other_staffs(world, make_request, api):
    pending = make_request(world.parent)
    mine = make_request(world.parent, S.ANDAMENTO, world.staff)
    other = make_request(world.parent, S.ANDAMENTO, world.other_staff)
    client = api(world.staff)

    assert ids(client.get(URL)) == {pending.pk, mine.pk}
    assert client.get(URL, {"id": pending.pk}).status_code == 200
    assert client.get(URL, {"id": mine.pk}).status_code == 200
    assert client.get(URL, {"id": other.pk}).status_code == 404


def test_admin_sees_everything(world, make_request, api):
    a = make_request(world.parent)
    b = make_request(world.other_parent, S.ANDAMENTO, world.staff)
    client = api(world.admin)
    assert ids(client.get(URL)) == {a.pk, b.pk}
    assert client.get(URL, {"id": b.pk}).status_code == 200


@pytest.mark.parametrize("who", ["user", "visitor"])
def test_other_roles_are_forbidden(world, make_request, api, who):
    form = make_request(world.parent)
    client = api(getattr(world, who))
    assert client.get(URL).status_code == 403
    assert client.get(URL, {"id": form.pk}).status_code == 403


def test_filters_apply_inside_the_visible_set(world, make_request, api):
    make_request(world.parent)
    answered = make_request(world.other_parent, S.ANDAMENTO, world.staff)
    client = api(world.admin)
    assert ids(client.get(URL, {"status": S.ANDAMENTO})) == {answered.pk}
    assert ids(client.get(URL, {"assigned_staff": world.staff.email})) == {answered.pk}
    assert client.get(URL, {"status": "nope"}).status_code == 400
    assert client.get(URL, {"id": "abc"}).status_code == 400
