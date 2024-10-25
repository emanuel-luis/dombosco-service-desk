from rest_framework import serializers
from allauth.account import app_settings as allauth_account_settings
from django.core.exceptions import ValidationError as DjangoValidationError
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.socialaccount.models import EmailAddress
from allauth.utils import get_username_max_length
from django.contrib.auth.models import Group, User
from django.contrib.auth import get_user_model

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
    groups = serializers.ListField(child=serializers.CharField(), required=False)

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
            "groups": self.validated_data.get("groups", []),
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

        groups = []
        for group_name in self.cleaned_data.get("groups"):
            try:
                group = Group.objects.get(name=group_name)
                groups.append(group)
            except Group.DoesNotExist as exc:
                raise serializers.ValidationError(f"Group {group_name} does not exist.")

        user.save()

        # add user to groups
        for group in groups:
            user.groups.add(group)
        user.save()

        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
