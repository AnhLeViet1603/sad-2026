from django.db import models

try:
    from pgvector.django import VectorField
except ImportError:
    VectorField = None


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent_id = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [("ACTIVE", "Active"), ("INACTIVE", "Inactive"), ("OUT_OF_STOCK", "Out of stock")]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField()
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    is_primary = models.BooleanField(default=False)


class Inventory(models.Model):
    product = models.OneToOneField(Product, related_name="inventory", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available_quantity(self):
        return max(self.quantity - self.reserved_quantity, 0)


class ProductAttribute(models.Model):
    name = models.CharField(max_length=100)
    code = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, related_name="attribute_values", on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)


class ProductEmbedding(models.Model):
    product = models.OneToOneField(Product, related_name="embedding", on_delete=models.CASCADE)
    document = models.TextField()
    embedding = VectorField(dimensions=384, null=True, blank=True) if VectorField else models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

