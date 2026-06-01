from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Shipment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_id", models.BigIntegerField(db_index=True)),
                ("user_id", models.BigIntegerField(db_index=True)),
                ("receiver_name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=20)),
                ("province", models.CharField(max_length=100)),
                ("district", models.CharField(max_length=100)),
                ("ward", models.CharField(max_length=100)),
                ("detail", models.TextField()),
                ("shipping_fee", models.DecimalField(decimal_places=2, default=30000, max_digits=12)),
                ("tracking_code", models.CharField(max_length=50, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("CREATED", "Created"),
                            ("PICKED_UP", "Picked up"),
                            ("IN_TRANSIT", "In transit"),
                            ("DELIVERED", "Delivered"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="CREATED",
                        max_length=30,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="ShippingStatusHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(max_length=30)),
                ("note", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "shipment",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="history", to="shipping.shipment"),
                ),
            ],
        ),
    ]

