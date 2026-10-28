from typing import Any

from django.contrib import admin
from django.http import HttpRequest

import forms.models


# ModelAdmin[...] is generic only in the stubs, not at runtime.
class ReadOnlyAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """List and detail views only: writes go through forms.services so they are logged."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False


class ParentsFormAdmin(ReadOnlyAdmin):
    list_display = [
        "responsible_party",
        "student",
        "briefing",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = ["status"]
    search_fields = ["responsible_party__email", "issue_description"]
    readonly_fields = ["created_at", "updated_at", "briefing"]
    ordering = ["status", "created_at"]


admin.site.register(forms.models.ParentForm, ParentsFormAdmin)
# admin.site.register(forms.models.StudentInformationSection)
# admin.site.register(forms.models.ParentForm)
admin.site.register(forms.models.StaffForm, ReadOnlyAdmin)


class RequestEventAdmin(ReadOnlyAdmin):
    """The log is append-only."""

    list_display = ["occurred_at", "request_id", "event_type", "actor_role", "source"]
    list_filter = ["event_type", "source"]
    ordering = ["-occurred_at"]


admin.site.register(forms.models.RequestEvent, RequestEventAdmin)
