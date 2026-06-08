from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from users.models import Address, User


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "full_name", "phone", "dob", "role", "is_active", "created_at"]
        read_only_fields = ["id", "username", "email", "role", "is_active", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "email", "password", "full_name", "phone", "dob"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "receiver_name",
            "phone",
            "province",
            "district",
            "ward",
            "detail",
            "is_default",
        ]
        read_only_fields = ["id"]
