from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    user_id = models.BigIntegerField(db_index=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="PENDING")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_id = models.BigIntegerField(null=True, blank=True)
    payment_status = models.CharField(max_length=30, default="PENDING")
    shipment_id = models.BigIntegerField(null=True, blank=True)
    shipping_status = models.CharField(max_length=30, default="CREATED")
    tracking_code = models.CharField(max_length=50, null=True, blank=True)
    receiver_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    detail = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_id = models.BigIntegerField()
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.URLField(null=True, blank=True)


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, related_name="history", on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

