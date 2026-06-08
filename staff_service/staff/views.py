from rest_framework.decorators import api_view

from common.permissions import require_admin, require_staff
from common.responses import error, ok
from common.views import health_response
from staff.models import Department, Permission, Role, Staff
from staff.serializers import DepartmentSerializer, PermissionSerializer, RoleSerializer, StaffSerializer


@api_view(["GET"])
def health(request):
    return health_response("staff_service")


def _serialize_or_error(serializer):
    if not serializer.is_valid():
        return None, error("VALIDATION_ERROR", serializer.errors, status=400)
    return serializer.save(), None


@api_view(["GET", "POST"])
def staff_collection(request):
    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        queryset = Staff.objects.all().order_by("id")
        return ok(StaffSerializer(queryset, many=True).data)

    auth_error = require_admin(request)
    if auth_error:
        return auth_error

    instance, response_error = _serialize_or_error(StaffSerializer(data=request.data))
    if response_error:
        return response_error
    return ok(StaffSerializer(instance).data, "Staff created", status=201)


@api_view(["GET", "PATCH", "DELETE"])
def staff_detail(request, staff_id):
    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    try:
        instance = Staff.objects.get(id=staff_id)
    except Staff.DoesNotExist:
        return error("STAFF_NOT_FOUND", "Staff not found", status=404)

    if request.method == "GET":
        return ok(StaffSerializer(instance).data)

    auth_error = require_admin(request)
    if auth_error:
        return auth_error

    if request.method == "DELETE":
        instance.delete()
        return ok({}, "Staff deleted")

    serializer = StaffSerializer(instance, data=request.data, partial=True)
    instance, response_error = _serialize_or_error(serializer)
    if response_error:
        return response_error
    return ok(StaffSerializer(instance).data, "Staff updated")


@api_view(["GET", "POST"])
def role_collection(request):
    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        queryset = Role.objects.all().order_by("id")
        return ok(RoleSerializer(queryset, many=True).data)

    auth_error = require_admin(request)
    if auth_error:
        return auth_error

    instance, response_error = _serialize_or_error(RoleSerializer(data=request.data))
    if response_error:
        return response_error
    return ok(RoleSerializer(instance).data, "Role created", status=201)


@api_view(["PATCH", "DELETE"])
def role_detail(request, role_id):
    auth_error = require_admin(request)
    if auth_error:
        return auth_error

    try:
        instance = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return error("ROLE_NOT_FOUND", "Role not found", status=404)

    if request.method == "DELETE":
        instance.delete()
        return ok({}, "Role deleted")

    serializer = RoleSerializer(instance, data=request.data, partial=True)
    instance, response_error = _serialize_or_error(serializer)
    if response_error:
        return response_error
    return ok(RoleSerializer(instance).data, "Role updated")


@api_view(["GET", "POST"])
def permission_collection(request):
    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        queryset = Permission.objects.all().order_by("id")
        return ok(PermissionSerializer(queryset, many=True).data)

    auth_error = require_admin(request)
    if auth_error:
        return auth_error

    instance, response_error = _serialize_or_error(PermissionSerializer(data=request.data))
    if response_error:
        return response_error
    return ok(PermissionSerializer(instance).data, "Permission created", status=201)


@api_view(["GET", "POST"])
def department_collection(request):
    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        queryset = Department.objects.all().order_by("id")
        return ok(DepartmentSerializer(queryset, many=True).data)

    auth_error = require_admin(request)
    if auth_error:
        return auth_error

    instance, response_error = _serialize_or_error(DepartmentSerializer(data=request.data))
    if response_error:
        return response_error
    return ok(DepartmentSerializer(instance).data, "Department created", status=201)


@api_view(["GET"])
def check_role(request):
    user_id = request.query_params.get("user_id") or request.user_id
    role_name = request.query_params.get("role")
    if not user_id or not role_name:
        return error("VALIDATION_ERROR", "`user_id` and `role` are required", status=400)

    has_role = Staff.objects.filter(user_id=user_id, is_active=True, roles__name=role_name).exists()
    return ok({"user_id": int(user_id), "role": role_name, "has_role": has_role})
