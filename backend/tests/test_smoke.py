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
