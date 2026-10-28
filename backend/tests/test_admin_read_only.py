import pytest
from django.contrib.auth import get_user_model

from forms.models import ParentForm, StaffForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client, make_request, world):
    form = make_request(world.parent, ParentForm.StatusChoices.ANDAMENTO, world.staff)
    root = get_user_model().objects.create_superuser("root@example.com", "pw-123456")
    client.force_login(root)
    return client, form


@pytest.mark.parametrize("model", ["parentform", "staffform"])
def test_forms_admin_is_read_only(admin_client, model):
    client, form = admin_client
    pk = form.pk if model == "parentform" else StaffForm.objects.get().pk
    base = f"/admin/forms/{model}/"
    assert client.get(base).status_code == 200
    assert client.get(f"{base}{pk}/change/").status_code == 200  # view only
    assert client.get(f"{base}add/").status_code == 403
    assert client.post(f"{base}{pk}/change/", {"status": 3}).status_code == 403
    assert client.get(f"{base}{pk}/delete/").status_code == 403
    assert client.post(f"{base}{pk}/delete/", {"post": "yes"}).status_code == 403
    form.refresh_from_db()
    assert form.status == ParentForm.StatusChoices.ANDAMENTO
