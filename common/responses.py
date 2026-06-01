from rest_framework.response import Response


def ok(data=None, message="OK", status=200):
    return Response({"success": True, "data": data or {}, "message": message}, status=status)


def error(code, message, status=400):
    return Response({"success": False, "error": {"code": code, "message": message}}, status=status)

