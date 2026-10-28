from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from core.utils import is_dom_bosco_staff, is_parent, is_superuser


class IsDomBoscoStaff(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return is_dom_bosco_staff(request.user, include_superuser=True)


class IsDomBoscoParent(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return is_parent(request.user, include_superuser=True)


class IsDomBoscoAdmin(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return is_superuser(request.user)
