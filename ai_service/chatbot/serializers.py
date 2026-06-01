from rest_framework import serializers


class TrackSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    event_type = serializers.ChoiceField(choices=["VIEWED", "ADDED_TO_CART", "PURCHASED", "RATED"])
    metadata = serializers.DictField(required=False)


class ChatSerializer(serializers.Serializer):
    message = serializers.CharField()
    session_id = serializers.IntegerField(required=False)

