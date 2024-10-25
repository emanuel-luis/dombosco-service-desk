from django.urls import include, path, re_path
from forms.views import *

urlpatterns = [
    path("parents/", ParentsFormViewAPI.as_view(), name="parents-form"),
    path("parents/update-status/", UpdateStatusParentsFormAPI.as_view(), name="parents-form-update-status"),
    path("parents/delete/", DeleteParentsFormAPI.as_view(), name="parents-form-delete"),
    path("staff/", StaffFormViewAPI.as_view(), name="staff-form"),
]
