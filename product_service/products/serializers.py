from rest_framework import serializers

from products.models import Category, Inventory, Product, ProductAttribute, ProductAttributeValue, ProductImage


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
            "images",
            "inventory",
            "attribute_values",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        inventory = validated_data.pop("inventory", None)
        attributes = validated_data.pop("attribute_values", [])
        product = Product.objects.create(**validated_data)
        Inventory.objects.create(product=product, **(inventory or {}))
        for image in images:
            ProductImage.objects.create(product=product, **image)
        for attribute in attributes:
            ProductAttributeValue.objects.create(product=product, **attribute)
        return product

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        inventory = validated_data.pop("inventory", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

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
