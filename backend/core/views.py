from rest_framework import permissions, views
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth.models import Group
from core.serializers import *
from core.permissions import *


class GroupViewAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated & IsDomBoscoAdmin]

    def get(self, request: Request):
        groups = Group.objects.all()

        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request):
        try:
            group = Group.objects.get(id=request.data.get("id"))
        except Group.DoesNotExist:
            return Response(
                {"error": "Group not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicationViewAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated & IsDomBoscoAdmin]

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated]
        return super().get_permissions()

    def get(self, request: Request):
        if is_superuser(request.user):
            applications = Application.objects.all()
        else:
            applications = Application.objects.filter(groups__user=request.user)

        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request):
        try:
            application = Application.objects.get(id=request.data.get("id"))
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
