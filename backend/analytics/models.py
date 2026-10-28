"""Read-only models over the PostgreSQL views created by migration 0001.

Layers: source (OLTP tables) -> raw (request_events) -> processed (v_request_lifecycle)
-> serving (the other views and the endpoints). The tables only exist on PostgreSQL.
"""

from django.db import models


class RequestLifecycle(models.Model):
    request_id = models.BigIntegerField(primary_key=True)
    opened_at = models.DateTimeField(null=True)
    first_response_at = models.DateTimeField(null=True)
    closed_at = models.DateTimeField(null=True)
    current_status = models.SmallIntegerField()
    deleted = models.BooleanField()
    hours_to_first_response = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    hours_to_close = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    class Meta:
        managed = False
        db_table = "v_request_lifecycle"


class DailyThroughput(models.Model):
    day = models.DateField(primary_key=True)
    opened = models.IntegerField()
    answered = models.IntegerField()
    finished = models.IntegerField()
    cancelled = models.IntegerField()

    class Meta:
        managed = False
        db_table = "v_daily_throughput"


class BacklogByStatus(models.Model):
    current_status = models.SmallIntegerField(primary_key=True)
    requests = models.IntegerField()
    oldest_opened_at = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = "v_backlog_by_status"


class SlaSummary(models.Model):
    id = models.SmallIntegerField(primary_key=True)  # always 1: the view has a single row
    responded_count = models.IntegerField()
    first_response_p50_hours = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    first_response_p90_hours = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    closed_count = models.IntegerField()
    close_p50_hours = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    close_p90_hours = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    class Meta:
        managed = False
        db_table = "v_sla_summary"
