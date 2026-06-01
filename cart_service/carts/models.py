from decimal import Decimal

from django.db import models


class Cart(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    status = models.CharField(max_length=30, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_amount(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product_id = models.BigIntegerField()
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product_id")

    @property
    def line_total(self):
        return self.product_price * self.quantity

