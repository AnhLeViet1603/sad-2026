from django.contrib import admin
from django.urls import path
from products import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    path("api/products", views.product_collection),
    path("api/products/search", views.product_search),
    path("api/products/ai/export", views.ai_export),
    path("api/products/<int:product_id>", views.product_detail),
    path("api/products/<int:product_id>/related", views.related_products),
    path("api/products/<int:product_id>/inventory", views.inventory_detail),
    path("api/products/ai/embedding/<int:product_id>", views.rebuild_embedding_placeholder),
    path("api/products/categories", views.category_collection),
    path("api/products/categories/<int:category_id>", views.category_detail),
]
