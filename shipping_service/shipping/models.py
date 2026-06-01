from django.db import models


class Shipment(models.Model):
    STATUS_CHOICES = [
        ("CREATED", "Created"),
        ("PICKED_UP", "Picked up"),
        ("IN_TRANSIT", "In transit"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    order_id = models.BigIntegerField(db_index=True)
    user_id = models.BigIntegerField(db_index=True)
    receiver_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    detail = models.TextField()
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=30000)
    tracking_code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ShippingStatusHistory(models.Model):
    shipment = models.ForeignKey(Shipment, related_name="history", on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

