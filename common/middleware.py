import jwt

from common.jwt_utils import decode_token, get_bearer_token


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_id = request.headers.get("X-User-Id")
        request.user_role = request.headers.get("X-User-Role")

        token = get_bearer_token(request)
        if token:
            try:
                payload = decode_token(token)
                if payload.get("type") == "access":
                    request.user_id = payload.get("user_id")
                    request.user_role = payload.get("role", "USER")
            except jwt.PyJWTError:
                pass

        return self.get_response(request)
