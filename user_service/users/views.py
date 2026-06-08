import jwt
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view

from common.jwt_utils import create_access_token, create_refresh_token, decode_token, get_bearer_token
from common.responses import error, ok
from common.views import health_response
from users.models import Address, RefreshToken, User
from users.serializers import AddressSerializer, LoginSerializer, RefreshSerializer, RegisterSerializer, UserPublicSerializer


@api_view(["GET"])
def health(request):
    return health_response("user_service")


def _require_user_id(request):
    if not request.user_id:
        return None, error("UNAUTHORIZED", "Authentication token is required", status=401)
    return int(request.user_id), None


def _token_pair(user):
    access_token = create_access_token(user.id, role=user.role)
    refresh_token = create_refresh_token(user.id, role=user.role)
    RefreshToken.objects.create(user_id=user.id, token=refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}


@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    user = serializer.save()
    return ok({"user": UserPublicSerializer(user).data, **_token_pair(user)}, "Registered", status=201)


@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    try:
        identifier = serializer.validated_data["email"]
        user = User.objects.get(Q(email=identifier) | Q(username=identifier), is_active=True)
    except User.DoesNotExist:
        return error("INVALID_CREDENTIALS", "Email or password is incorrect", status=401)

    if not check_password(serializer.validated_data["password"], user.password):
        return error("INVALID_CREDENTIALS", "Email or password is incorrect", status=401)

    return ok({"user": UserPublicSerializer(user).data, **_token_pair(user)}, "Logged in")


@api_view(["POST"])
def refresh(request):
    serializer = RefreshSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    token = serializer.validated_data["refresh_token"]
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        return error("INVALID_TOKEN", "Refresh token is invalid or expired", status=401)

    if payload.get("type") != "refresh":
        return error("INVALID_TOKEN", "Refresh token type is invalid", status=401)

    token_record = RefreshToken.objects.filter(token=token, is_revoked=False).first()
    if token_record is None:
        return error("INVALID_TOKEN", "Refresh token has been revoked", status=401)

    access_token = create_access_token(payload["user_id"], role=payload.get("role", "USER"))
    return ok({"access_token": access_token, "token_type": "Bearer"})


@api_view(["POST"])
def logout(request):
    token = request.data.get("refresh_token") or get_bearer_token(request)
    if not token:
        return error("VALIDATION_ERROR", "A refresh token or bearer token is required", status=400)

    updated = RefreshToken.objects.filter(token=token, is_revoked=False).update(
        is_revoked=True,
        revoked_at=timezone.now(),
    )
    return ok({"revoked": updated > 0}, "Logged out")


@api_view(["GET", "PATCH"])
def me(request):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error

    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return error("USER_NOT_FOUND", "User not found", status=404)

    if request.method == "GET":
        return ok(UserPublicSerializer(user).data)

    serializer = UserPublicSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    serializer.save()
    return ok(serializer.data, "Profile updated")


@api_view(["GET", "POST"])
def addresses(request):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        queryset = Address.objects.filter(user_id=user_id).order_by("-is_default", "id")
        return ok(AddressSerializer(queryset, many=True).data)

    serializer = AddressSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    with transaction.atomic():
        if serializer.validated_data.get("is_default"):
            Address.objects.filter(user_id=user_id, is_default=True).update(is_default=False)
        address = serializer.save(user_id=user_id)

    return ok(AddressSerializer(address).data, "Address created", status=201)


@api_view(["PATCH", "DELETE"])
def address_detail(request, address_id):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error

    try:
        address = Address.objects.get(id=address_id, user_id=user_id)
    except Address.DoesNotExist:
        return error("ADDRESS_NOT_FOUND", "Address not found", status=404)

    if request.method == "DELETE":
        address.delete()
        return ok({}, "Address deleted")

    serializer = AddressSerializer(address, data=request.data, partial=True)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    with transaction.atomic():
        if serializer.validated_data.get("is_default"):
            Address.objects.filter(user_id=user_id, is_default=True).exclude(id=address.id).update(is_default=False)
        serializer.save()

    return ok(serializer.data, "Address updated")


@api_view(["GET"])
def verify_token(request):
    token = get_bearer_token(request)
    if not token:
        return error("UNAUTHORIZED", "Authentication token is required", status=401)

    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        return error("INVALID_TOKEN", "Token is invalid or expired", status=401)

    return ok({"valid": True, "payload": payload})
