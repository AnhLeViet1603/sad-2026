from rest_framework import serializers

from payments.models import Payment, PaymentTransaction


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ["id", "status", "message", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    transactions = PaymentTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "user_id",
            "amount",
            "method",
            "status",
            "provider_reference",
            "transactions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "provider_reference", "transactions", "created_at", "updated_at"]


class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    user_id = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    method = serializers.CharField(max_length=50, default="COD")

