from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    order_id = models.BigIntegerField(db_index=True)
    user_id = models.BigIntegerField(db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=50, default="COD")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="PENDING")
    provider_reference = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PaymentTransaction(models.Model):
    payment = models.ForeignKey(Payment, related_name="transactions", on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    message = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

