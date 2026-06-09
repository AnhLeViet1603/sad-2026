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

    @property
    def product_type(self):
        for related_name in PRODUCT_TYPE_RELATED_NAMES:
            if hasattr(self, related_name):
                return PRODUCT_TYPE_LABELS[related_name]
        return "product"


class Book(Product):
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    isbn = models.CharField(max_length=30, unique=True, null=True, blank=True)
    language = models.CharField(max_length=80, default="Vietnamese")
    page_count = models.PositiveIntegerField(default=0)


class Laptop(Product):
    cpu = models.CharField(max_length=120)
    ram_gb = models.PositiveIntegerField(default=8)
    storage_gb = models.PositiveIntegerField(default=256)
    gpu = models.CharField(max_length=120, null=True, blank=True)
    screen_size_inch = models.DecimalField(max_digits=4, decimal_places=1, default=14)


class Phone(Product):
    os = models.CharField(max_length=80)
    storage_gb = models.PositiveIntegerField(default=128)
    ram_gb = models.PositiveIntegerField(default=6)
    camera_mp = models.PositiveIntegerField(default=12)
    battery_mah = models.PositiveIntegerField(default=4000)


class Toy(Product):
    age_range = models.CharField(max_length=80)
    material = models.CharField(max_length=120, null=True, blank=True)
    safety_standard = models.CharField(max_length=120, null=True, blank=True)


class Tablet(Product):
    os = models.CharField(max_length=80)
    screen_size_inch = models.DecimalField(max_digits=4, decimal_places=1, default=10)
    storage_gb = models.PositiveIntegerField(default=128)
    supports_pen = models.BooleanField(default=False)


class Headphones(Product):
    connection_type = models.CharField(max_length=80, default="Bluetooth")
    noise_cancelling = models.BooleanField(default=False)
    battery_hours = models.PositiveIntegerField(default=0)


class Camera(Product):
    sensor_type = models.CharField(max_length=120)
    megapixels = models.DecimalField(max_digits=5, decimal_places=1)
    lens_mount = models.CharField(max_length=120, null=True, blank=True)
    video_resolution = models.CharField(max_length=80, null=True, blank=True)


class SmartWatch(Product):
    os = models.CharField(max_length=80)
    battery_days = models.PositiveIntegerField(default=1)
    water_resistant = models.BooleanField(default=False)
    health_features = models.CharField(max_length=255, null=True, blank=True)


class HomeAppliance(Product):
    appliance_type = models.CharField(max_length=120)
    power_watts = models.PositiveIntegerField(default=0)
    capacity = models.CharField(max_length=120, null=True, blank=True)
    energy_rating = models.CharField(max_length=40, null=True, blank=True)


class Clothing(Product):
    size = models.CharField(max_length=40)
    color = models.CharField(max_length=80)
    material = models.CharField(max_length=120, null=True, blank=True)
    gender = models.CharField(max_length=40, null=True, blank=True)


PRODUCT_TYPE_RELATED_NAMES = [
    "book",
    "laptop",
    "phone",
    "toy",
    "tablet",
    "headphones",
    "camera",
    "smartwatch",
    "homeappliance",
    "clothing",
]

PRODUCT_TYPE_LABELS = {
    "book": "book",
    "laptop": "laptop",
    "phone": "phone",
    "toy": "toy",
    "tablet": "tablet",
    "headphones": "headphones",
    "camera": "camera",
    "smartwatch": "smart_watch",
    "homeappliance": "home_appliance",
    "clothing": "clothing",
}


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
