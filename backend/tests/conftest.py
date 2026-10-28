from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import connection
from rest_framework.test import APIClient

from forms import services
from forms.models import ParentForm

REQUEST_DATA = {
    "requested_by": 0,
    "student_name": "Aluno",
    "student_birth_date": "2015-01-01",
    "student_grade_year": 3,
    "student_class_name": "A",
    "relationship_to_student": 0,
    "issue_description": "Preciso de ajuda",
}


@pytest.fixture(autouse=True)
def fast_password_hasher(settings):
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def auth_groups(db):
    call_command("loaddata", "fixtures/auth.yaml")


@pytest.fixture
def make_user(auth_groups):
    def make(email, group=None, **extra):
        user = get_user_model().objects.create_user(
            email=email, username=email, password="pw-123456", **extra
        )
        if group:
            user.groups.add(Group.objects.get(name=group))
        return user

    return make


@pytest.fixture
def world(make_user):
    """One user per role, plus a second parent and a second staff member."""
    return SimpleNamespace(
        admin=make_user("admin@example.com", "Administrador"),
        staff=make_user("staff@example.com", "Colaborador"),
        other_staff=make_user("staff2@example.com", "Colaborador"),
        parent=make_user("parent@example.com", "Responsável"),
        other_parent=make_user("parent2@example.com", "Responsável"),
        user=make_user("user@example.com", "Usuário"),
        visitor=make_user("visitor@example.com", "Visitante"),
    )


@pytest.fixture
def make_request():
    """A request owned by `owner`, advanced to `status` through the real services."""

    def make(owner, status=ParentForm.StatusChoices.PENDENTE, staff=None):
        form = services.create_request(owner, dict(REQUEST_DATA))
        if status != ParentForm.StatusChoices.PENDENTE:
            assert staff is not None
            services.answer_request(staff, form.pk, {})
            form.refresh_from_db()
            if status != ParentForm.StatusChoices.ANDAMENTO:
                services.change_status(staff, form.pk, status)
                form.refresh_from_db()
        return form

    return make


@pytest.fixture
def api():
    def client(user=None):
        client = APIClient()
        if user is not None:
            client.force_authenticate(user)
        return client

    return client


def pytest_collection_modifyitems(config, items):
    """Skip `postgres` tests (triggers and the like) unless the database is PostgreSQL."""
    if connection.vendor == "postgresql":
        return
    skip = pytest.mark.skip(reason="needs PostgreSQL")
    for item in items:
        if "postgres" in item.keywords:
            item.add_marker(skip)
