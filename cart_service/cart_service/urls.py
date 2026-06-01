from django.contrib import admin
from django.urls import path
from carts import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    path("api/cart", views.current_cart),
    path("api/cart/items", views.add_item),
    path("api/cart/items/<int:item_id>", views.item_detail),
    path("api/cart/clear", views.clear_cart),
    path("api/cart/checkout-data", views.checkout_data),
]
