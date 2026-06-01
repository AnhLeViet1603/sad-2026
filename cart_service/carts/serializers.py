from rest_framework import serializers

from carts.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "product_name", "product_price", "quantity", "image_url", "line_total"]
        read_only_fields = ["id", "product_name", "product_price", "image_url", "line_total"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user_id", "status", "items", "total_amount", "created_at", "updated_at"]
        read_only_fields = ["id", "user_id", "status", "items", "total_amount", "created_at", "updated_at"]


class AddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

