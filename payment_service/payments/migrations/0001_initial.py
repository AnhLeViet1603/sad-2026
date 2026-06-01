from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_id", models.BigIntegerField(db_index=True)),
                ("user_id", models.BigIntegerField(db_index=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("method", models.CharField(default="COD", max_length=50)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("SUCCESS", "Success"),
                            ("FAILED", "Failed"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="PENDING",
                        max_length=30,
                    ),
                ),
                ("provider_reference", models.CharField(blank=True, max_length=100, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(max_length=30)),
                ("message", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "payment",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="payments.payment"),
                ),
            ],
        ),
    ]

