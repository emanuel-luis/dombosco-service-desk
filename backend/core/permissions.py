from rest_framework import permissions
from rest_framework.request import Request

from core.utils import *


class IsDomBoscoStaff(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        return is_dom_bosco_staff(request.user, include_superuser=True)


class IsDomBoscoParent(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        return is_parent(request.user, include_superuser=True)


class IsDomBoscoAdmin(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        return is_superuser(request.user)
