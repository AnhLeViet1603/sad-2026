from django.contrib import admin
from django.urls import path
from shipping import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    path("api/shipping/fee", views.shipping_fee),
    path("api/shipping/shipments", views.shipment_collection),
    path("api/shipping/shipments/<int:shipment_id>", views.shipment_detail),
    path("api/shipping/shipments/<int:shipment_id>/status", views.update_status),
    path("api/shipping/tracking/<str:tracking_code>", views.tracking),
]
