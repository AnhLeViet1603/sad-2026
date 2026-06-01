from django.contrib import admin
from django.urls import path, re_path
from proxy import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    re_path(r"^api/(?P<path>.*)$", views.proxy),
]
