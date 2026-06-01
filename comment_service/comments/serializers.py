from rest_framework import serializers

from comments.models import CommentReply, Review


class CommentReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReply
        fields = ["id", "review", "user_id", "content", "created_at"]
        read_only_fields = ["id", "user_id", "created_at"]


class ReviewSerializer(serializers.ModelSerializer):
    replies = CommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product_id", "user_id", "rating", "title", "content", "replies", "created_at", "updated_at"]
        read_only_fields = ["id", "user_id", "replies", "created_at", "updated_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class ReplySerializer(serializers.Serializer):
    content = serializers.CharField()

