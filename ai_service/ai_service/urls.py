from django.contrib import admin
from django.urls import path
from chatbot import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", views.health),
    path("api/ai/sync-products", views.sync_products),
    path("api/ai/track", views.track),
    path("api/ai/recommendations/home", views.home_recommendations),
    path("api/ai/chat", views.chat),
]
