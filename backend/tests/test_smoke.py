import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from rest_framework.test import APIClient


def test_django_check_passes():
    call_command("check")


@pytest.mark.django_db
def test_no_pending_migrations():
    call_command("makemigrations", "--check", "--dry-run")


@pytest.mark.django_db
def test_protected_endpoint_rejects_anonymous():
    response = APIClient().get("/api/v1/core/groups/")
    assert response.status_code == 401


def test_auth_fixture_creates_five_groups(auth_groups):
    assert Group.objects.count() == 5


@pytest.mark.parametrize("path", ["/swagger.json", "/swagger/", "/redoc/"])
def test_api_docs_endpoints_return_200(path):
    assert APIClient().get(path).status_code == 200


def test_healthz_is_public_and_ok(db):
    response = APIClient().get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthz_is_503_when_the_database_is_down(db):
    from unittest import mock

    from django.db import OperationalError, connection

    with mock.patch.object(connection, "cursor", side_effect=OperationalError("down")):
        assert APIClient().get("/healthz").status_code == 503
