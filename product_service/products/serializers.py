from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from products.models import (
    Book,
    Camera,
    Category,
    Clothing,
    Headphones,
    HomeAppliance,
    Inventory,
    Laptop,
    Phone,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
    SmartWatch,
    Tablet,
    Toy,
)


PRODUCT_TYPE_CONFIG = {
    "book": {
        "model": Book,
        "fields": ["author", "publisher", "isbn", "language", "page_count"],
    },
    "laptop": {
        "model": Laptop,
        "fields": ["cpu", "ram_gb", "storage_gb", "gpu", "screen_size_inch"],
    },
    "phone": {
        "model": Phone,
        "fields": ["os", "storage_gb", "ram_gb", "camera_mp", "battery_mah"],
    },
    "toy": {
        "model": Toy,
        "fields": ["age_range", "material", "safety_standard"],
    },
    "tablet": {
        "model": Tablet,
        "fields": ["os", "screen_size_inch", "storage_gb", "supports_pen"],
    },
    "headphones": {
        "model": Headphones,
        "fields": ["connection_type", "noise_cancelling", "battery_hours"],
    },
    "camera": {
        "model": Camera,
        "fields": ["sensor_type", "megapixels", "lens_mount", "video_resolution"],
    },
    "smart_watch": {
        "model": SmartWatch,
        "fields": ["os", "battery_days", "water_resistant", "health_features"],
        "related_name": "smartwatch",
    },
    "home_appliance": {
        "model": HomeAppliance,
        "fields": ["appliance_type", "power_watts", "capacity", "energy_rating"],
        "related_name": "homeappliance",
    },
    "clothing": {
        "model": Clothing,
        "fields": ["size", "color", "material", "gender"],
    },
}

PRODUCT_TYPE_DEFAULTS = {
    "book": {"author": "Unknown author", "language": "Vietnamese", "page_count": 0},
    "laptop": {"cpu": "Unknown CPU", "ram_gb": 8, "storage_gb": 256, "screen_size_inch": "14.0"},
    "phone": {"os": "Android", "storage_gb": 128, "ram_gb": 6, "camera_mp": 12, "battery_mah": 4000},
    "toy": {"age_range": "3+", "material": "Mixed"},
    "tablet": {"os": "Android", "screen_size_inch": "10.0", "storage_gb": 128, "supports_pen": False},
    "headphones": {"connection_type": "Bluetooth", "noise_cancelling": False, "battery_hours": 12},
    "camera": {"sensor_type": "CMOS", "megapixels": "24.0"},
    "smart_watch": {"os": "Wear OS", "battery_days": 1, "water_resistant": False},
    "home_appliance": {"appliance_type": "General", "power_watts": 0},
    "clothing": {"size": "M", "color": "Black"},
}

for key, config in PRODUCT_TYPE_CONFIG.items():
    config.setdefault("related_name", key)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent_id"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "alt_text", "is_primary"]


class InventorySerializer(serializers.ModelSerializer):
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Inventory
        fields = ["quantity", "reserved_quantity", "available_quantity", "updated_at"]
        read_only_fields = ["updated_at"]


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ["id", "name", "code"]


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute = ProductAttributeSerializer(read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttribute.objects.all(),
        source="attribute",
        write_only=True,
    )

    class Meta:
        model = ProductAttributeValue
        fields = ["id", "attribute", "attribute_id", "value"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    images = ProductImageSerializer(many=True, required=False)
    inventory = InventorySerializer(required=False)
    attribute_values = ProductAttributeValueSerializer(many=True, required=False)
    product_type = serializers.ChoiceField(choices=list(PRODUCT_TYPE_CONFIG), write_only=True, required=False)
    type = serializers.SerializerMethodField()
    type_details = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "category",
            "category_id",
            "brand",
            "status",
            "created_at",
            "product_type",
            "type",
            "type_details",
            "images",
            "inventory",
            "attribute_values",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        inventory = validated_data.pop("inventory", None)
        attributes = validated_data.pop("attribute_values", [])
        product_type = validated_data.pop("product_type", "book")
        type_details = self.initial_data.get("type_details") or {}
        type_config = PRODUCT_TYPE_CONFIG[product_type]
        model_class = type_config["model"]
        child_data = self._child_data(type_config, type_details)
        product = model_class.objects.create(**validated_data, **child_data)
        Inventory.objects.create(product=product, **(inventory or {}))
        for image in images:
            ProductImage.objects.create(product=product, **image)
        for attribute in attributes:
            ProductAttributeValue.objects.create(product=product, **attribute)
        return product

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        inventory = validated_data.pop("inventory", None)
        product_type = validated_data.pop("product_type", None)
        current_type = self.get_type(instance)
        if product_type and product_type != current_type:
            raise serializers.ValidationError({"product_type": "Changing product_type is not supported."})
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        type_details = self.initial_data.get("type_details")
        if type_details is not None and current_type in PRODUCT_TYPE_CONFIG:
            child = self._child_instance(instance, PRODUCT_TYPE_CONFIG[current_type])
            if child:
                for field, value in self._child_data(PRODUCT_TYPE_CONFIG[current_type], type_details).items():
                    setattr(child, field, value)
                child.save()

        if images is not None:
            primary_image = images[0] if images else None
            if primary_image:
                primary_defaults = {
                    "image_url": primary_image["image_url"],
                    "alt_text": primary_image.get("alt_text"),
                }
                image_instance, _ = ProductImage.objects.update_or_create(
                    product=instance,
                    is_primary=True,
                    defaults=primary_defaults,
                )
                ProductImage.objects.filter(product=instance).exclude(id=image_instance.id).delete()
                instance._prefetched_objects_cache = {}
            else:
                ProductImage.objects.filter(product=instance).delete()
                instance._prefetched_objects_cache = {}

        if inventory is not None:
            inventory_instance, _ = Inventory.objects.update_or_create(product=instance, defaults=inventory)
            instance._state.fields_cache["inventory"] = inventory_instance

        return instance

    def get_type(self, product):
        for product_type, config in PRODUCT_TYPE_CONFIG.items():
            if self._child_instance(product, config):
                return product_type
        return "product"

    def get_type_details(self, product):
        product_type = self.get_type(product)
        config = PRODUCT_TYPE_CONFIG.get(product_type)
        child = self._child_instance(product, config) if config else None
        if not child:
            return {}
        details = {}
        for field in config["fields"]:
            value = getattr(child, field)
            details[field] = str(value) if hasattr(value, "as_tuple") else value
        return details

    def _child_instance(self, product, config):
        if not config:
            return None
        try:
            return getattr(product, config["related_name"])
        except (AttributeError, ObjectDoesNotExist):
            return None

    def _child_data(self, config, details):
        product_type = next(key for key, value in PRODUCT_TYPE_CONFIG.items() if value is config)
        data = dict(PRODUCT_TYPE_DEFAULTS.get(product_type, {}))
        data.update({field: details[field] for field in config["fields"] if field in details})
        return data
