from django.contrib import admin
from django.urls import path
from payments import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    path("api/payments", views.payment_collection),
    path("api/payments/callback", views.callback),
    path("api/payments/<int:payment_id>", views.payment_detail),
    path("api/payments/<int:payment_id>/simulate-success", views.simulate_success),
    path("api/payments/<int:payment_id>/simulate-failed", views.simulate_failed),
]
