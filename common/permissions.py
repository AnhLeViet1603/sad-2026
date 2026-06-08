from common.responses import error


ADMIN_ROLES = {"ADMIN"}
STAFF_ROLES = {"ADMIN", "STAFF", "PRODUCT_MANAGER", "ORDER_MANAGER"}


def role_name(request):
    role = getattr(request, "user_role", None) or request.headers.get("X-User-Role")
    return str(role).upper() if role else None


def user_id(request):
    value = getattr(request, "user_id", None) or request.headers.get("X-User-Id")
    try:
        return int(value) if value else None
    except (TypeError, ValueError):
        return None


def require_user(request):
    current_user_id = user_id(request)
    if not current_user_id:
        return None, error("UNAUTHORIZED", "Authentication token is required", status=401)
    return current_user_id, None


def require_roles(request, allowed_roles):
    current_role = role_name(request)
    if not current_role:
        return error("UNAUTHORIZED", "Authentication token is required", status=401)
    if current_role not in allowed_roles:
        return error("FORBIDDEN", "You do not have permission to perform this action", status=403)
    return None


def require_admin(request):
    return require_roles(request, ADMIN_ROLES)


def require_staff(request):
    return require_roles(request, STAFF_ROLES)
