from rest_framework import serializers

from orders.models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product_id", "product_name", "product_price", "quantity", "line_total", "image_url"]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ["id", "status", "note", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user_id",
            "status",
            "total_amount",
            "shipping_fee",
            "payment_id",
            "payment_status",
            "shipment_id",
            "shipping_status",
            "tracking_code",
            "receiver_name",
            "phone",
            "province",
            "district",
            "ward",
            "detail",
            "items",
            "history",
            "created_at",
            "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    payment_method = serializers.CharField(max_length=50, default="COD")
    shipping_address = serializers.DictField()

    def validate_shipping_address(self, value):
        required = ["receiver_name", "phone", "province", "district", "ward", "detail"]
        missing = [field for field in required if not value.get(field)]
        if missing:
            raise serializers.ValidationError(f"Missing fields: {', '.join(missing)}")
        return value


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["PENDING", "CONFIRMED", "PROCESSING", "SHIPPED", "COMPLETED", "CANCELLED"])
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)

