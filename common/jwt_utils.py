import datetime

import jwt
from django.conf import settings


ACCESS_TOKEN_HOURS = 2
REFRESH_TOKEN_DAYS = 7


def _now():
    return datetime.datetime.now(datetime.UTC)


def create_access_token(user_id, role="USER"):
    issued_at = _now()
    payload = {
        "user_id": user_id,
        "role": role,
        "type": "access",
        "exp": issued_at + datetime.timedelta(hours=ACCESS_TOKEN_HOURS),
        "iat": issued_at,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def create_refresh_token(user_id, role="USER"):
    issued_at = _now()
    payload = {
        "user_id": user_id,
        "role": role,
        "type": "refresh",
        "exp": issued_at + datetime.timedelta(days=REFRESH_TOKEN_DAYS),
        "iat": issued_at,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])


def get_bearer_token(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return header.removeprefix("Bearer ").strip()

