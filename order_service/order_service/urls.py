from django.contrib import admin
from django.urls import path
from orders import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    path("api/orders", views.order_collection),
    path("api/orders/checkout", views.checkout),
    path("api/orders/<int:order_id>", views.order_detail),
    path("api/orders/<int:order_id>/status", views.update_status),
]
