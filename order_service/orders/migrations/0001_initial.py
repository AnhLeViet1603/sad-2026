from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.BigIntegerField(db_index=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("CONFIRMED", "Confirmed"),
                            ("PROCESSING", "Processing"),
                            ("SHIPPED", "Shipped"),
                            ("COMPLETED", "Completed"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="PENDING",
                        max_length=30,
                    ),
                ),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("shipping_fee", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("payment_id", models.BigIntegerField(blank=True, null=True)),
                ("payment_status", models.CharField(default="PENDING", max_length=30)),
                ("shipment_id", models.BigIntegerField(blank=True, null=True)),
                ("shipping_status", models.CharField(default="CREATED", max_length=30)),
                ("tracking_code", models.CharField(blank=True, max_length=50, null=True)),
                ("receiver_name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=20)),
                ("province", models.CharField(max_length=100)),
                ("district", models.CharField(max_length=100)),
                ("ward", models.CharField(max_length=100)),
                ("detail", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_id", models.BigIntegerField()),
                ("product_name", models.CharField(max_length=255)),
                ("product_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("quantity", models.PositiveIntegerField()),
                ("line_total", models.DecimalField(decimal_places=2, max_digits=12)),
                ("image_url", models.URLField(blank=True, null=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.order")),
            ],
        ),
        migrations.CreateModel(
            name="OrderStatusHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(max_length=30)),
                ("note", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="history", to="orders.order")),
            ],
        ),
    ]

