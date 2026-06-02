from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=255)),
                ("full_name", models.CharField(max_length=255)),
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                ("dob", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="RefreshToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.BigIntegerField(db_index=True)),
                ("token", models.CharField(max_length=255, unique=True)),
                ("is_revoked", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.BigIntegerField(db_index=True)),
                ("receiver_name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=20)),
                ("province", models.CharField(max_length=100)),
                ("district", models.CharField(max_length=100)),
                ("ward", models.CharField(max_length=100)),
                ("detail", models.TextField()),
                ("is_default", models.BooleanField(default=False)),
            ],
        ),
    ]
