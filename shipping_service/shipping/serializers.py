from rest_framework import serializers

from shipping.models import Shipment, ShippingStatusHistory


class ShippingStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingStatusHistory
        fields = ["id", "status", "note", "created_at"]


class ShipmentSerializer(serializers.ModelSerializer):
    history = ShippingStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id",
            "order_id",
            "user_id",
            "receiver_name",
            "phone",
            "province",
            "district",
            "ward",
            "detail",
            "shipping_fee",
            "tracking_code",
            "status",
            "history",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tracking_code", "status", "history", "created_at", "updated_at"]


class CreateShipmentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    user_id = serializers.IntegerField(min_value=1)
    receiver_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20)
    province = serializers.CharField(max_length=100)
    district = serializers.CharField(max_length=100)
    ward = serializers.CharField(max_length=100)
    detail = serializers.CharField()
    shipping_fee = serializers.DecimalField(max_digits=12, decimal_places=2, default=30000)


class UpdateShipmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["CREATED", "PICKED_UP", "IN_TRANSIT", "DELIVERED", "CANCELLED"])
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)


class ShippingFeeSerializer(serializers.Serializer):
    province = serializers.CharField(max_length=100, required=False, allow_blank=True)
    district = serializers.CharField(max_length=100, required=False, allow_blank=True)

