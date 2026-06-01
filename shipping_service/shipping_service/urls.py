from django.contrib import admin
from django.urls import path
from shipping.views import health


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health),
]

