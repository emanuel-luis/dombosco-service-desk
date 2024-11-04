from core.serializers import UserProfileSerializer
from core.utils import has_comment_permission
from forms.models import *
from rest_framework import serializers


class ParentQuerySerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=ParentForm.objects.all(), required=False)
    status = serializers.ChoiceField(choices=ParentForm.StatusChoices.choices, required=False)
    assigned_staff = serializers.EmailField(required=False)
    responsible_party = serializers.EmailField(required=False)


class ParentsFormSerializer(serializers.ModelSerializer):
    responsible_party = UserProfileSerializer(read_only=True)

    class Meta:
        model = ParentForm
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "status", "id"]

    def create(self, validated_data):
        validated_data["responsible_party"] = self.context["request"].user
        return super().create(validated_data)


class ParentsFormListSerializer(serializers.ModelSerializer):
    responsible_party = serializers.EmailField(read_only=True)
    issue_description = serializers.CharField(read_only=True, source="briefing")
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ParentForm
        fields = [
            "id",
            "responsible_party",
            "issue_description",
            "status",
            "created_at",
            "updated_at",
            "assigned_staff",
        ]
        read_only_fields = [
            "id",
            "issue_description",
            "status",
            "created_at",
            "updated_at",
            "assigned_staff",
        ]


class StaffFormSerializer(serializers.ModelSerializer):
    assigned_staff = UserProfileSerializer(read_only=True)
    parent_form_id = serializers.PrimaryKeyRelatedField(queryset=ParentForm.objects.all(), write_only=True, source="parent_form")

    class Meta:
        model = StaffForm
        exclude = ["parent_form"]

    def create(self, validated_data):
        validated_data["assigned_staff"] = self.context["request"].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True, source="user.full_name")
    parent_form_id = serializers.PrimaryKeyRelatedField(queryset=ParentForm.objects.all(), write_only=True, source="parent_form")

    class Meta:
        model = Comment
        exclude = ["parent_form"]
        read_only_fields = ["created_at", "updated_at", "id"]

    def validate_parent_form_id(self, value: ParentForm):
        if value.status == ParentForm.StatusChoices.PENDENTE:
            raise serializers.ValidationError("It is not possible to add comments to a form that is pending.")

        if not has_comment_permission(self.context["request"].user, value):
            raise serializers.ValidationError("You do not have permission to add comments to this form.")

        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
