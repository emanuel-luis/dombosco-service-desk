from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from core.permissions import IsDomBoscoParent

pytestmark = pytest.mark.django_db


def make_user(email, group=None):
    user = get_user_model().objects.create_user(email=email, password="pw-123456")
    if group:
        user.groups.add(Group.objects.get(name=group))
    return user


@pytest.mark.parametrize("group", ["Usuário", "Visitante", None])
def test_non_parent_never_passes_even_in_debug(auth_groups, settings, group):
    settings.DEBUG = True
    user = make_user("someone@example.com", group)
    assert not IsDomBoscoParent().has_permission(SimpleNamespace(user=user), None)


def test_parent_passes(auth_groups, settings):
    settings.DEBUG = False
    user = make_user("parent@example.com", "Responsável")
    assert IsDomBoscoParent().has_permission(SimpleNamespace(user=user), None)
