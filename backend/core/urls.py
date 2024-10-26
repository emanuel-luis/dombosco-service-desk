from django.urls import include, path, re_path
from core.views import *

urlpatterns = [
    path("groups/", GroupViewAPI.as_view(), name="groups"),
    path("applications/", ApplicationViewAPI.as_view(), name="applications"),
]
