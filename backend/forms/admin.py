from django.contrib import admin
import forms.models


class ParentsFormAdmin(admin.ModelAdmin):
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
admin.site.register(forms.models.StaffForm)
