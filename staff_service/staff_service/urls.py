from django.contrib import admin
from django.urls import path
from staff.views import health


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health),
]

