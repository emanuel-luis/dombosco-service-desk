from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.socialaccount.models import EmailAddress
from allauth.utils import get_username_max_length
from core.models import Application
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

User = get_user_model()


class UserProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    phone = serializers.CharField(read_only=True)
    mobile_phone = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "mobile_phone"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_account_settings.USERNAME_MIN_LENGTH,
        required=allauth_account_settings.USERNAME_REQUIRED,
    )
    email = serializers.EmailField(required=allauth_account_settings.EMAIL_REQUIRED)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20, required=False)
    mobile_phone = serializers.CharField(max_length=20, required=False)

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and EmailAddress.objects.is_verified(email) or User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user is already registered with this e-mail address.")
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "phone": self.validated_data.get("phone", ""),
            "mobile_phone": self.validated_data.get("mobile_phone", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data["password1"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(detail=serializers.as_serializer_error(exc))
        user.phone = self.cleaned_data.get("phone")
        user.mobile_phone = self.cleaned_data.get("mobile_phone")
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.save()

        if user.email.endswith(settings.DOM_BOSCO_EMAIL_DOMAIN):
            group, _ = Group.objects.get_or_create(name="Colaborador")
        else:
            group, _ = Group.objects.get_or_create(name="Responsável")
        user.groups.add(group)
        user.save()

        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"
        read_only_fields = ["id", "name"]


class ApplicationSerializer(serializers.ModelSerializer):
    groups_id = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=Group.objects.all()), write_only=True, source="groups")

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data: dict):
        groups = validated_data.pop("groups")
        application = Application.objects.create(**validated_data)
        for group in groups:
            application.groups.add(group)
        return application

    def update(self, instance: Application, validated_data: dict):
        groups = validated_data.pop("groups")
        instance = super().update(instance, validated_data)
        instance.groups.clear()
        for group in groups:
            instance.groups.add(group)
        return instance
