import pytest
from allauth.account.models import EmailAddress
from django.core.management import call_command
from django.core.management.base import CommandError

from core.models import User
from forms.models import ParentForm, RequestEvent


@pytest.fixture
def allowed(monkeypatch, auth_groups):
    monkeypatch.setenv("ALLOW_DEMO_SEED", "true")
    monkeypatch.setenv("DEMO_PASSWORD", "seed-test-pw")


def test_refuses_without_the_flag(monkeypatch, auth_groups):
    monkeypatch.delenv("ALLOW_DEMO_SEED", raising=False)
    with pytest.raises(CommandError, match="ALLOW_DEMO_SEED"):
        call_command("seed_demo")
    assert not User.objects.exists()


def test_creates_verified_users_and_seed_events(allowed):
    call_command("seed_demo")
    assert User.objects.filter(email__endswith="@demo.example").count() == 8
    assert EmailAddress.objects.filter(verified=True, primary=True).count() == 8
    assert User.objects.get(email="admin@demo.example").check_password("seed-test-pw")
    assert ParentForm.objects.count() == 60
    events = RequestEvent.objects.all()
    assert events.exists()
    assert set(events.values_list("source", flat=True)) == {"seed"}


def test_is_idempotent(allowed):
    call_command("seed_demo")
    requests, events = ParentForm.objects.count(), RequestEvent.objects.count()
    call_command("seed_demo")
    assert (ParentForm.objects.count(), RequestEvent.objects.count()) == (requests, events)
