from django.db import models


class Review(models.Model):
    product_id = models.BigIntegerField(db_index=True)
    user_id = models.BigIntegerField(db_index=True)
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CommentReply(models.Model):
    review = models.ForeignKey(Review, related_name="replies", on_delete=models.CASCADE)
    user_id = models.BigIntegerField(db_index=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

