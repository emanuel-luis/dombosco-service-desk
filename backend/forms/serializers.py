from rest_framework import serializers

from core.serializers import UserProfileSerializer
from forms.models import Comment, ParentForm, StaffForm


class IdQuerySerializer(serializers.Serializer):
    id = serializers.IntegerField()


class ParentQuerySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    status = serializers.ChoiceField(choices=ParentForm.StatusChoices.choices, required=False)
    assigned_staff = serializers.EmailField(required=False)
    responsible_party = serializers.EmailField(required=False)


class ParentsFormSerializer(serializers.ModelSerializer):
    responsible_party = UserProfileSerializer(read_only=True)

    class Meta:
        model = ParentForm
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "status", "id"]


class StatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ParentForm.StatusChoices.choices)


class StatusChangeResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=ParentForm.StatusChoices.choices)
    detail = serializers.CharField()


class StaffFormSerializer(serializers.ModelSerializer):
    """Output of a staff answer."""

    assigned_staff = UserProfileSerializer(read_only=True)

    class Meta:
        model = StaffForm
        exclude = ["parent_form"]


class StaffFormUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffForm
        fields = ["school_advice", "actions_taken", "final_notes"]


class StaffFormCreateSerializer(StaffFormUpdateSerializer):
    parent_form_id = serializers.IntegerField()

    class Meta(StaffFormUpdateSerializer.Meta):
        fields = [*StaffFormUpdateSerializer.Meta.fields, "parent_form_id"]


class CommentSerializer(serializers.ModelSerializer):
    """Output of a comment."""

    user = serializers.CharField(read_only=True, source="user.full_name")

    class Meta:
        model = Comment
        exclude = ["parent_form"]


class CommentUpdateSerializer(serializers.Serializer):
    comment = serializers.CharField()


class CommentCreateSerializer(CommentUpdateSerializer):
    parent_form_id = serializers.IntegerField()
