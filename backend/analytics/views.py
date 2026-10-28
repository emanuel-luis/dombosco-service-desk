"""Admin-only read endpoints over the analytics views.

The views exist only on PostgreSQL, so on any other database the endpoints answer 501.
The permission check runs first (401 anonymous, 403 other groups); the 501 comes after
the query parameters are validated.
"""

from django.db import connection
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status, views
from rest_framework.exceptions import APIException
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from analytics.models import BacklogByStatus, DailyThroughput, RequestLifecycle, SlaSummary
from analytics.serializers import (
    BacklogByStatusSerializer,
    DailyThroughputSerializer,
    RequestLifecycleSerializer,
    SlaSummarySerializer,
    ThroughputQuerySerializer,
)
from core.permissions import IsDomBoscoAdmin
from forms.exceptions import RequestInvalid

ADMIN_ONLY = [permissions.IsAuthenticated & IsDomBoscoAdmin]
NOT_POSTGRES = OpenApiResponse(description="The database is not PostgreSQL.")


class AnalyticsUnavailable(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = "Analytics views need a PostgreSQL database."
    default_code = "not_implemented"


def require_postgres() -> None:
    if connection.vendor != "postgresql":
        raise AnalyticsUnavailable()


class LifecyclePagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000


class RequestsView(generics.ListAPIView[RequestLifecycle]):
    """One row per request seen in the event log (v_request_lifecycle), by request id."""

    permission_classes = ADMIN_ONLY
    serializer_class = RequestLifecycleSerializer
    pagination_class = LifecyclePagination
    queryset = RequestLifecycle.objects.order_by("request_id")

    @extend_schema(responses={200: RequestLifecycleSerializer(many=True), 501: NOT_POSTGRES})
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        require_postgres()
        return super().list(request, *args, **kwargs)


class ThroughputView(views.APIView):
    permission_classes = ADMIN_ONLY

    @extend_schema(
        parameters=[ThroughputQuerySerializer],
        responses={200: DailyThroughputSerializer(many=True), 501: NOT_POSTGRES},
        description=(
            "Requests opened, answered, finished and cancelled per UTC day, oldest first. "
            "Days with none of those events have no row. `from` and `to` (YYYY-MM-DD) are "
            "inclusive and optional."
        ),
    )
    def get(self, request: Request) -> Response:
        query = ThroughputQuerySerializer(data=request.query_params)
        if not query.is_valid():
            raise RequestInvalid("from and to must be dates as YYYY-MM-DD.")
        first, last = query.validated_data.get("from"), query.validated_data.get("to")
        if first and last and first > last:
            raise RequestInvalid("from must not be after to.")
        require_postgres()
        rows = DailyThroughput.objects.order_by("day")
        if first:
            rows = rows.filter(day__gte=first)
        if last:
            rows = rows.filter(day__lte=last)
        return Response(DailyThroughputSerializer(rows, many=True).data)


class BacklogView(views.APIView):
    permission_classes = ADMIN_ONLY

    @extend_schema(
        responses={200: BacklogByStatusSerializer(many=True), 501: NOT_POSTGRES},
        description="Count and oldest opening per current status, deleted requests excluded.",
    )
    def get(self, request: Request) -> Response:
        require_postgres()
        rows = BacklogByStatus.objects.order_by("current_status")
        return Response(BacklogByStatusSerializer(rows, many=True).data)


class SlaView(views.APIView):
    permission_classes = ADMIN_ONLY

    @extend_schema(
        responses={200: SlaSummarySerializer, 501: NOT_POSTGRES},
        description=(
            "Median and 90th percentile of the hours to first response and to close, with "
            "counts, over requests that were not deleted. Percentiles are null with no data."
        ),
    )
    def get(self, request: Request) -> Response:
        require_postgres()
        return Response(SlaSummarySerializer(SlaSummary.objects.get()).data)
