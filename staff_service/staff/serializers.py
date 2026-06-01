from rest_framework import serializers

from staff.models import Department, Permission, Role, Staff


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "code", "name"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False,
    )

    class Meta:
        model = Role
        fields = ["id", "name", "permissions"]


class StaffSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all(), required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Staff
        fields = ["id", "user_id", "employee_code", "department", "roles", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

