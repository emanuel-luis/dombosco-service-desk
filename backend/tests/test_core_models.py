import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def test_create_user_works_when_domain_is_unset(settings):
    settings.DOM_BOSCO_EMAIL_DOMAIN = None
    user = get_user_model().objects.create_user(email="a@example.com", password="pw-123456")
    assert not user.groups.exists()


def test_create_user_never_grants_colaborador_from_the_typed_email(settings):
    settings.DOM_BOSCO_EMAIL_DOMAIN = "@dombosco.test"
    user = get_user_model().objects.create_user(email="a@dombosco.test", password="pw-123456")
    assert not user.groups.exists()


def test_other_domain_user_gets_no_group(settings):
    settings.DOM_BOSCO_EMAIL_DOMAIN = "@dombosco.test"
    user = get_user_model().objects.create_user(email="a@example.com", password="pw-123456")
    assert not user.groups.exists()


@pytest.mark.parametrize(
    ("setting", "email", "expected"),
    [
        ("@dombosco.test", "staff@dombosco.test", True),
        ("dombosco.test", "staff@DomBosco.Test", True),
        ("dombosco.test", "student@aluno.dombosco.test", True),
        ("dombosco.test", "someone@evildombosco.test", False),
        ("dombosco.test", "someone@dombosco.test.example.com", False),
        ("", "staff@dombosco.test", False),
    ],
)
def test_has_staff_email_matches_the_domain_part_only(settings, setting, email, expected):
    settings.DOM_BOSCO_EMAIL_DOMAIN = setting
    user = get_user_model()(email=email)
    assert user.has_staff_email is expected
