from rest_framework.decorators import api_view

from common.views import health_response


@api_view(["GET"])
def health(request):
    return health_response("comment_service")

