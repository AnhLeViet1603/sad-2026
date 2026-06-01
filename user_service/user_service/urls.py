from django.contrib import admin
from django.urls import path
from users import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    path("api/users/register", views.register),
    path("api/users/login", views.login),
    path("api/users/refresh", views.refresh),
    path("api/users/logout", views.logout),
    path("api/users/me", views.me),
    path("api/users/addresses", views.addresses),
    path("api/users/addresses/<int:address_id>", views.address_detail),
    path("api/users/verify-token", views.verify_token),
]
