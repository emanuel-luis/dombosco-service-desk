"""
URL configuration for dombosco_atendimento project.

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

from django.contrib import admin
from django.urls import include, path, re_path
from allauth.account.views import ConfirmEmailView
from accounts.views import GoogleLogin, GoogleLoginCallback, LoginPage

from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

api_routers = routers.DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", LoginPage.as_view(), name="login"),
    path("api/v1/", include(api_routers.urls)),
    path("api/v1/forms/", include("forms.urls")),
    path("api/v1/admin/", include("core.urls")),
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/google/", GoogleLogin.as_view(), name="google_login"),
    path(
        "api/v1/auth/google/callback/",
        GoogleLoginCallback.as_view(),
        name="google_login_callback",
    ),
    re_path(
        "^api/v1/auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$",
        ConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
]
