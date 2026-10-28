import pytest
from django.core.management import call_command

from core.models import Application

pytestmark = pytest.mark.django_db


def test_core_fixture_loads():
    call_command("loaddata", "fixtures/core.yaml")
    application = Application.objects.get(pk=1)
    assert application.mdm_id
    assert application.name == "Administrador"
