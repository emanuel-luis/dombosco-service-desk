from typing import Any

from rest_framework import serializers


def _hours() -> serializers.DecimalField:
    return serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False, allow_null=True, read_only=True
    )


class RequestLifecycleSerializer(serializers.Serializer[Any]):
    request_id = serializers.IntegerField()
    opened_at = serializers.DateTimeField(allow_null=True)
    first_response_at = serializers.DateTimeField(allow_null=True)
    closed_at = serializers.DateTimeField(allow_null=True)
    current_status = serializers.IntegerField(
        help_text="0 pending, 1 in progress, 2 done, 3 cancelled."
    )
    deleted = serializers.BooleanField()
    hours_to_first_response = _hours()
    hours_to_close = _hours()


class DailyThroughputSerializer(serializers.Serializer[Any]):
    day = serializers.DateField(help_text="UTC day.")
    opened = serializers.IntegerField()
    answered = serializers.IntegerField()
    finished = serializers.IntegerField()
    cancelled = serializers.IntegerField()


class BacklogByStatusSerializer(serializers.Serializer[Any]):
    current_status = serializers.IntegerField()
    requests = serializers.IntegerField()
    oldest_opened_at = serializers.DateTimeField(allow_null=True)


class SlaSummarySerializer(serializers.Serializer[Any]):
    responded_count = serializers.IntegerField()
    first_response_p50_hours = _hours()
    first_response_p90_hours = _hours()
    closed_count = serializers.IntegerField()
    close_p50_hours = _hours()
    close_p90_hours = _hours()


# `from` is a Python keyword, so the declared fields are attached through type().
ThroughputQuerySerializer = type(
    "ThroughputQuerySerializer",
    (serializers.Serializer,),
    {
        "from": serializers.DateField(required=False, help_text="First UTC day, inclusive."),
        "to": serializers.DateField(required=False, help_text="Last UTC day, inclusive."),
    },
)
