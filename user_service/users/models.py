from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Address(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    receiver_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    detail = models.TextField()
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.receiver_name} - {self.phone}"


class RefreshToken(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    token = models.CharField(max_length=255, unique=True)
    is_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
