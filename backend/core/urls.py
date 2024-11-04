from core.views import *
from django.urls import path

urlpatterns = [
    path("groups/", GroupViewAPI.as_view(), name="groups"),
    path("applications/", ApplicationViewAPI.as_view(), name="applications"),
]
