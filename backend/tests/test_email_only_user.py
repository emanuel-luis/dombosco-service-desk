import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

PASSWORD = "Sup3r-secret-pw"


def test_two_users_can_be_created_without_a_username():
    manager = get_user_model().objects
    manager.create_user(email="a@example.com", password=PASSWORD)
    manager.create_user(email="b@example.com", password=PASSWORD)
    assert manager.count() == 2


def test_two_registrations_without_username_both_succeed(settings):
    settings.ACCOUNT_EMAIL_VERIFICATION = "none"
    client = APIClient()
    for email in ("a@example.com", "b@example.com"):
        response = client.post(
            "/api/v1/auth/registration/",
            {"email": email, "password1": PASSWORD, "password2": PASSWORD},
            format="json",
        )
        assert response.status_code == 201, response.content


def test_login_by_email_still_works(settings):
    settings.ACCOUNT_EMAIL_VERIFICATION = "none"
    get_user_model().objects.create_user(email="a@example.com", password=PASSWORD)
    response = APIClient().post(
        "/api/v1/auth/login/", {"email": "a@example.com", "password": PASSWORD}, format="json"
    )
    assert response.status_code == 200, response.content


def test_user_admin_add_and_change_pages_render(client):
    admin = get_user_model().objects.create_superuser(email="root@example.com", password=PASSWORD)
    client.force_login(admin)
    assert client.get("/admin/core/user/add/").status_code == 200
    assert client.get(f"/admin/core/user/{admin.pk}/change/").status_code == 200
    assert client.get("/admin/core/user/").status_code == 200


def test_user_admin_can_add_a_user(client):
    admin = get_user_model().objects.create_superuser(email="root@example.com", password=PASSWORD)
    client.force_login(admin)
    response = client.post(
        "/admin/core/user/add/",
        {"email": "new@example.com", "password1": PASSWORD, "password2": PASSWORD},
    )
    assert response.status_code == 302, response.content
    assert get_user_model().objects.filter(email="new@example.com").exists()
