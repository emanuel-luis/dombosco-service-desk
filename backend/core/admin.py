from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import Application, User


# UserAdmin and ModelAdmin are generic only in the stubs, not at runtime.
class UserAdmin(BaseUserAdmin):  # type: ignore[type-arg]
    model = User
    list_display = (
        "email",
        "full_name",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone", "mobile_phone")},
        ),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class ApplicationAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    model = Application
    list_display = (
        "mdm_id",
        "name",
        "description",
    )
    search_fields = ("name",)
    ordering = ("name",)


# Deleting a user here cascades to their requests and comments without writing request_events
# (the log covers app/API writes only).
admin.site.register(User, UserAdmin)
admin.site.register(Application, ApplicationAdmin)
