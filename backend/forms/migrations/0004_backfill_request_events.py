from django.db import migrations

from forms.backfill import backfill


def forwards(apps, schema_editor):
    backfill(apps)


def backwards(apps, schema_editor):
    # The only place request_events rows are deleted. The historical model has a plain
    # manager (no append-only guard), and the Postgres trigger (migration 0005) is already
    # dropped when this runs, because 0005 is reversed first.
    apps.get_model("forms", "RequestEvent").objects.filter(source="backfill").delete()


class Migration(migrations.Migration):
    dependencies = [("forms", "0003_request_event")]

    operations = [migrations.RunPython(forwards, backwards)]
