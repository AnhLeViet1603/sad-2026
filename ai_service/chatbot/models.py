from django.db import models
from pgvector.django import VectorField


class ProductDocument(models.Model):
    product_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    product_type = models.CharField(max_length=80, null=True, blank=True)
    type_details = models.JSONField(default=dict, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    document = models.TextField(default="")
    embedding = VectorField(dimensions=3072, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserBehavior(models.Model):
    EVENT_CHOICES = [
        ("VIEWED", "Viewed"),
        ("ADDED_TO_CART", "Added to cart"),
        ("PURCHASED", "Purchased"),
        ("RATED", "Rated"),
    ]

    user_id = models.BigIntegerField(db_index=True)
    product_id = models.BigIntegerField(db_index=True)
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RecommendationLog(models.Model):
    user_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    query = models.TextField(null=True, blank=True)
    product_ids = models.JSONField(default=list)
    source = models.CharField(max_length=50, default="mock")
    created_at = models.DateTimeField(auto_now_add=True)


class ChatSession(models.Model):
    user_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    content = models.TextField()
    products = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
