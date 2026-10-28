import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

URL = "/api/v1/auth/user/"


def make_user(email, *groups, **extra):
    user = get_user_model().objects.create_user(email=email, password="pw-123456", **extra)
    user.groups.add(*Group.objects.filter(name__in=groups))
    return user


def details(user):
    client = APIClient()
    client.force_authenticate(user)
    response = client.get(URL)
    assert response.status_code == 200
    return response.json()


@pytest.mark.parametrize(
    ("groups", "extra", "role"),
    [
        (("Administrador",), {}, "admin"),
        ((), {"is_superuser": True}, "admin"),
        ((), {"is_staff": True}, "admin"),
        (("Colaborador",), {}, "staff"),
        (("Responsável",), {}, "parent"),
        (("Usuário",), {}, "user"),
        (("Visitante",), {}, "visitor"),
        ((), {}, "visitor"),
        (("Colaborador", "Responsável", "Administrador"), {}, "admin"),
        (("Responsável", "Colaborador"), {}, "staff"),
        (("Usuário", "Responsável"), {}, "parent"),
    ],
)
def test_role_follows_precedence(auth_groups, groups, extra, role):
    data = details(make_user("u@example.com", *groups, **extra))
    assert data["role"] == role
    assert sorted(data["groups"]) == sorted(groups)
    assert data["email"] == "u@example.com"


def test_anonymous_is_rejected():
    assert APIClient().get(URL).status_code == 401
