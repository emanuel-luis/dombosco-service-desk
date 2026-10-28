"""Answers and comments say which request they belong to, and comments say who wrote them."""

import pytest

from forms import services
from forms.models import ParentForm
from tests.conftest import REQUEST_DATA

pytestmark = pytest.mark.django_db

S = ParentForm.StatusChoices


def test_staff_answer_exposes_its_request(world, api):
    form = services.create_request(world.parent, dict(REQUEST_DATA))
    services.answer_request(world.staff, form.pk, {})
    response = api(world.staff).get("/api/v1/forms/staff/")
    assert response.status_code == 200
    assert [row["parent_form_id"] for row in response.json()] == [form.pk]


def test_comment_exposes_author_id_and_request(world, api):
    form = services.create_request(world.parent, dict(REQUEST_DATA))
    services.answer_request(world.staff, form.pk, {})
    services.add_comment(world.parent, form.pk, "obrigado")
    response = api(world.parent).get(f"/api/v1/forms/comment/?id={form.pk}")
    assert response.status_code == 200
    (row,) = response.json()
    assert row["user_id"] == world.parent.pk
    assert row["parent_form_id"] == form.pk
    assert isinstance(row["user"], str)
