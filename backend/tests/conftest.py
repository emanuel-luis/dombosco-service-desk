import pytest
from django.core.management import call_command


@pytest.fixture
def auth_groups(db):
    call_command("loaddata", "fixtures/auth.yaml")
