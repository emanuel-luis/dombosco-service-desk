from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, views
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import Application
from core.permissions import IsDomBoscoAdmin
from core.serializers import ApplicationSerializer, GroupSerializer
from core.utils import authenticated_user, is_superuser

if TYPE_CHECKING:
    # Stub-only protocol: it does not exist at runtime.
    from rest_framework.permissions import _SupportsHasPermission


class GroupViewAPI(views.APIView):
    """Read-only list of the groups. They come from fixtures/auth.yaml and the permission checks
    rely on their names, so they are managed in the Django admin, not through the API."""

    permission_classes = [permissions.IsAuthenticated & IsDomBoscoAdmin]

    @extend_schema(responses={200: GroupSerializer(many=True)})
    def get(self, request: Request) -> Response:
        groups = Group.objects.all()

        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)


class ApplicationViewAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated & IsDomBoscoAdmin]

    def get_permissions(self) -> "Sequence[_SupportsHasPermission]":
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(responses={200: ApplicationSerializer(many=True)})
    def get(self, request: Request) -> Response:
        if is_superuser(authenticated_user(request)):
            applications = Application.objects.all()
        else:
            applications = Application.objects.filter(groups__user=authenticated_user(request))

        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    @extend_schema(request=ApplicationSerializer, responses={201: ApplicationSerializer})
    def post(self, request: Request) -> Response:
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=ApplicationSerializer,
        responses=ApplicationSerializer,
        description="The target is given by `id` in the body.",
    )
    def put(self, request: Request) -> Response:
        body: Any = request.data  # request boundary: the body is only validated further down
        try:
            application = Application.objects.get(id=body.get("id"))
        except Application.DoesNotExist:
            return Response(
                {"error": "Application not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ApplicationSerializer(application, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
