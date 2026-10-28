import re

import pytest
from allauth.account.models import EmailAddress
from django.core import mail
from django.core.cache import cache
from rest_framework.test import APIClient

from core.utils import is_dom_bosco_staff

pytestmark = pytest.mark.django_db


def register(client, email, verification="mandatory", settings=None):
    response = client.post(
        "/api/v1/auth/registration/",
        {"email": email, "password1": "Sup3r-secret-pw", "password2": "Sup3r-secret-pw"},
        format="json",
    )
    assert response.status_code in (200, 201, 204), response.content
    return EmailAddress.objects.get(email=email).user


def confirm(client):
    match = re.search(r"http\S*/account-confirm-email/[-:\w]+/", str(mail.outbox[-1].body))
    assert match
    return client.get(match.group(0).split("testserver", 1)[-1])


@pytest.fixture
def domain(settings):
    cache.clear()  # allauth rate-limits confirmation emails per address
    settings.DOM_BOSCO_EMAIL_DOMAIN = "@dombosco.test"
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    return settings


def groups(user):
    return set(user.groups.values_list("name", flat=True))


def test_staff_domain_registration_is_not_staff_before_confirmation(domain):
    user = register(APIClient(), "fake@dombosco.test")
    assert "Colaborador" not in groups(user)
    assert not is_dom_bosco_staff(user)


def test_confirmation_grants_colaborador(domain):
    client = APIClient()
    user = register(client, "real@dombosco.test")
    assert confirm(client).status_code == 302
    assert groups(user) == {"Colaborador"}
    assert is_dom_bosco_staff(user)


def test_optional_verification_still_leaves_unconfirmed_user_non_staff(domain):
    domain.ACCOUNT_EMAIL_VERIFICATION = "optional"
    user = register(APIClient(), "fake@dombosco.test")
    assert not is_dom_bosco_staff(user)
    assert "Colaborador" not in groups(user)


def test_confirming_a_non_staff_domain_grants_nothing(domain):
    client = APIClient()
    user = register(client, "parent@example.com")
    assert confirm(client).status_code == 302
    assert groups(user) == {"Responsável"}
    assert not is_dom_bosco_staff(user)


def test_confirm_in_the_signup_session_does_not_500(domain):
    # Same client for signup and confirmation: allauth reverses "account_login" here.
    client = APIClient()
    register(client, "parent@example.com")
    assert confirm(client).status_code == 302
