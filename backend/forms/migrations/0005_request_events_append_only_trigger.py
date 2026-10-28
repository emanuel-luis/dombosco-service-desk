from django.db import migrations

CREATE = """
CREATE FUNCTION request_events_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'request_events is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER request_events_append_only
BEFORE UPDATE OR DELETE ON request_events
FOR EACH ROW EXECUTE FUNCTION request_events_append_only();
"""

DROP = """
DROP TRIGGER IF EXISTS request_events_append_only ON request_events;
DROP FUNCTION IF EXISTS request_events_append_only();
"""


def create_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(CREATE)


def drop_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(DROP)


class Migration(migrations.Migration):
    # TRUNCATE is not covered on purpose: test flushes need it.
    dependencies = [("forms", "0004_backfill_request_events")]

    operations = [migrations.RunPython(create_trigger, drop_trigger)]
