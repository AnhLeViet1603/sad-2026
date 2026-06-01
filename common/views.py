from common.responses import ok


def health_response(service_name):
    return ok({"service": service_name, "status": "healthy"})

