from django.urls import path

from core.views import *

urlpatterns = [
    path("groups/", GroupViewAPI.as_view(), name="groups"),
    path("applications/", ApplicationViewAPI.as_view(), name="applications"),
]
