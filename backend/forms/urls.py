from django.urls import include, path, re_path
from forms.views import *

urlpatterns = [
    path("parents/", ParentsFormViewAPI.as_view(), name="parents-form"),
    path("parents/choices/", ParentFormsChoicesViewAPI.as_view(), name="parents-form-choices"),
    path("parents/update-status/", UpdateStatusParentsFormAPI.as_view(), name="parents-form-update-status"),
    path("staff/", StaffFormViewAPI.as_view(), name="staff-form"),
]
