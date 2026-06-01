from django.contrib import admin
from django.urls import path
from comments import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    path("api/comments/reviews", views.review_collection),
    path("api/comments/products/<int:product_id>/reviews", views.product_reviews),
    path("api/comments/products/<int:product_id>/summary", views.rating_summary),
    path("api/comments/reviews/<int:review_id>/replies", views.reply_review),
]
