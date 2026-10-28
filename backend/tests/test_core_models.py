import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def test_create_user_works_when_domain_is_unset(settings):
    settings.DOM_BOSCO_EMAIL_DOMAIN = None
    user = get_user_model().objects.create_user(email="a@example.com", password="pw-123456")
    assert not user.groups.exists()


def test_staff_domain_user_joins_colaborador_group(settings):
    settings.DOM_BOSCO_EMAIL_DOMAIN = "@dombosco.test"
    user = get_user_model().objects.create_user(email="a@dombosco.test", password="pw-123456")
    assert list(user.groups.values_list("name", flat=True)) == ["Colaborador"]


def test_other_domain_user_gets_no_group(settings):
    settings.DOM_BOSCO_EMAIL_DOMAIN = "@dombosco.test"
    user = get_user_model().objects.create_user(email="a@example.com", password="pw-123456")
    assert not user.groups.exists()
