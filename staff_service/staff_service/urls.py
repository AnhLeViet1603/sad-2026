from django.contrib import admin
from django.urls import path
from staff import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    path("api/staff", views.staff_collection),
    path("api/staff/<int:staff_id>", views.staff_detail),
    path("api/staff/roles", views.role_collection),
    path("api/staff/roles/<int:role_id>", views.role_detail),
    path("api/staff/permissions", views.permission_collection),
    path("api/staff/departments", views.department_collection),
    path("api/staff/check-role", views.check_role),
]
