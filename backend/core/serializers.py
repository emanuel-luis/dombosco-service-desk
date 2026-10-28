from typing import Any

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.socialaccount.models import EmailAddress
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpRequest
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import Application, User
from core.utils import ROLES, get_role

_signup_fields = allauth_account_settings.SIGNUP_FIELDS


class UserProfileSerializer(serializers.Serializer[dict[str, Any]]):
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    phone = serializers.CharField(read_only=True)
    mobile_phone = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "mobile_phone"]


class UserWithRoleSerializer(UserDetailsSerializer):  # type: ignore[misc]  # dj_rest_auth is untyped
    """/auth/user/ payload plus the group names and a single role for the frontend."""

    groups: serializers.SlugRelatedField[Group] = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    role = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ChoiceField(choices=ROLES))
    def get_role(self, user: User) -> str:
        return get_role(user)

    class Meta(UserDetailsSerializer.Meta):  # type: ignore[misc]  # dj_rest_auth is untyped
        fields = (*UserDetailsSerializer.Meta.fields, "groups", "role")
        read_only_fields = (*UserDetailsSerializer.Meta.read_only_fields, "groups", "role")


class RegisterSerializer(serializers.Serializer[dict[str, Any]]):
    email = serializers.EmailField(required=_signup_fields["email"]["required"])
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20, required=False)
    mobile_phone = serializers.CharField(max_length=20, required=False)

    def validate_email(self, email: str) -> str:
        email = get_adapter().clean_email(email)
        if (
            email
            and EmailAddress.objects.is_verified(email)
            or User.objects.filter(email=email).exists()
        ):
            raise serializers.ValidationError(
                "A user is already registered with this e-mail address."
            )
        return email

    def validate_password1(self, password: str) -> str:
        cleaned: str = get_adapter().clean_password(password)
        return cleaned

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data

    def custom_signup(self, request: HttpRequest, user: User) -> None:
        pass

    def get_cleaned_data(self) -> dict[str, Any]:
        return {
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "phone": self.validated_data.get("phone", ""),
            "mobile_phone": self.validated_data.get("mobile_phone", ""),
        }

    # dj_rest_auth calls save(request), unlike the DRF save(**kwargs) it overrides.
    def save(self, request: HttpRequest) -> User:  # type: ignore[override]
        adapter = get_adapter()
        user: User = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data["password1"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(detail=serializers.as_serializer_error(exc))
        user.phone = self.cleaned_data.get("phone")
        user.mobile_phone = self.cleaned_data.get("mobile_phone")
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()

        # Colaborador is granted only after the email is confirmed (see core.signals).
        group, _ = Group.objects.get_or_create(name="Responsável")
        user.groups.add(group)
        user.save()

        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class GroupSerializer(serializers.ModelSerializer[Group]):
    class Meta:
        model = Group
        fields = "__all__"
        read_only_fields = ["id", "name"]


class ApplicationSerializer(serializers.ModelSerializer[Application]):
    groups_id = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Group.objects.all()),
        write_only=True,
        source="groups",
    )

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data: dict[str, Any]) -> Application:
        groups = validated_data.pop("groups")
        application = Application.objects.create(**validated_data)
        for group in groups:
            application.groups.add(group)
        return application

    def update(self, instance: Application, validated_data: dict[str, Any]) -> Application:
        groups = validated_data.pop("groups")
        instance = super().update(instance, validated_data)
        instance.groups.clear()
        for group in groups:
            instance.groups.add(group)
        return instance
