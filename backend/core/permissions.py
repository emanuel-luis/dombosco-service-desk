from core.utils import *
from django.conf import settings
from rest_framework import permissions
from rest_framework.request import Request


class IsDomBoscoStaff(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        return is_dom_bosco_staff(request.user, include_superuser=True)


class IsDomBoscoParent(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        return settings.DEBUG or is_parent(request.user, include_superuser=True)


class IsDomBoscoAdmin(permissions.BasePermission):
    def has_permission(self, request: Request, view):
        return is_superuser(request.user)
