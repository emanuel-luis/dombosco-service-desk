"""
This file contains the urls for the forms app.
"""

from django.urls import path

from forms.views import (
    CommentViewAPI,
    ParentFormsChoicesViewAPI,
    ParentFormViewAPI,
    StaffFormViewAPI,
    UpdateStatusParentFormAPI,
)

urlpatterns = [
    path("parent/", ParentFormViewAPI.as_view(), name="parent-form"),
    path("parent/choices/", ParentFormsChoicesViewAPI.as_view(), name="parent-form-choices"),
    path(
        "parent/update-status/",
        UpdateStatusParentFormAPI.as_view(),
        name="parent-form-update-status",
    ),
    path("staff/", StaffFormViewAPI.as_view(), name="staff-form"),
    path("comment/", CommentViewAPI.as_view(), name="comments"),
]
