"""
URL configuration for dombosco_service_desk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from allauth.account.views import ConfirmEmailView
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from dombosco_service_desk.health import healthz

api_routers = routers.DefaultRouter()

urlpatterns = [
    path("healthz", healthz, name="healthz"),
    path("swagger.json", SpectacularJSONAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="schema-swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="schema-redoc"),
    path("admin/", admin.site.urls),
    # allauth reverses "account_login" after confirming an email in the signup session;
    # login lives in the frontend, so send it there.
    path("account/login/", RedirectView.as_view(url=settings.LOGIN_URL), name="account_login"),
    path("api/v1/", include(api_routers.urls)),
    path("api/v1/forms/", include("forms.urls")),
    path("api/v1/core/", include("core.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    re_path(
        r"^api/v1/auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$",
        ConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
]

if settings.GOOGLE_OAUTH_CLIENT_ID:
    from accounts.views import GoogleLogin

    urlpatterns.append(path("api/v1/auth/google/", GoogleLogin.as_view(), name="google_login"))
