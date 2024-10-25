from forms.models import ParentForm, StaffForm
from rest_framework import serializers
from core.serializers import UserProfileSerializer


class ParentsFormSerializer(serializers.ModelSerializer):
    responsible_party = UserProfileSerializer(read_only=True)

    class Meta:
        model = ParentForm
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "status", "id"]

    def get_staff_form(self, obj: ParentForm):
        staff_form = StaffForm.objects.filter(parent_form=obj).first()
        if staff_form:
            return StaffFormSerializer(staff_form).data
        return {}

    def create(self, validated_data):
        validated_data["responsible_party"] = self.context["request"].user
        return super().create(validated_data)


class ParentsFormListSerializer(serializers.ModelSerializer):
    responsible_party = serializers.EmailField(read_only=True)
    assigned_staff = serializers.SerializerMethodField(read_only=True)
    issue_description = serializers.CharField(read_only=True, source="briefing")
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ParentForm
        fields = ["id", "responsible_party", "issue_description", "status", "created_at", "updated_at", "assigned_staff"]
        read_only_fields = ["id", "issue_description", "status", "created_at", "updated_at", "assigned_staff"]

    def get_assigned_staff(self, obj: ParentForm):
        staff_form = StaffForm.objects.filter(parent_form=obj).first()
        if staff_form:
            return staff_form.assigned_staff.email
        return None


class StaffFormSerializer(serializers.ModelSerializer):
    assigned_staff = UserProfileSerializer(read_only=True)
    parent_form = ParentsFormSerializer(read_only=True)
    parent_form_id = serializers.PrimaryKeyRelatedField(queryset=ParentForm.objects.all(), write_only=True, source="parent_form")

    class Meta:
        model = StaffForm
        fields = "__all__"

    def create(self, validated_data):
        validated_data["assigned_staff"] = self.context["request"].user
        return super().create(validated_data)

    def get_parent_form(self, obj: StaffForm):
        return ParentsFormSerializer(obj.parent_form)
