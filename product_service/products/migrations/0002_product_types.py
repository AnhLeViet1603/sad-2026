from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("author", models.CharField(max_length=255)),
                ("publisher", models.CharField(blank=True, max_length=255, null=True)),
                ("isbn", models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ("language", models.CharField(default="Vietnamese", max_length=80)),
                ("page_count", models.PositiveIntegerField(default=0)),
            ],
            bases=("products.product",),
        ),
        migrations.CreateModel(
            name="Laptop",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("cpu", models.CharField(max_length=120)),
                ("ram_gb", models.PositiveIntegerField(default=8)),
                ("storage_gb", models.PositiveIntegerField(default=256)),
                ("gpu", models.CharField(blank=True, max_length=120, null=True)),
                ("screen_size_inch", models.DecimalField(decimal_places=1, default=14, max_digits=4)),
            ],
            bases=("products.product",),
        ),
        migrations.CreateModel(
            name="Phone",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("os", models.CharField(max_length=80)),
                ("storage_gb", models.PositiveIntegerField(default=128)),
                ("ram_gb", models.PositiveIntegerField(default=6)),
                ("camera_mp", models.PositiveIntegerField(default=12)),
                ("battery_mah", models.PositiveIntegerField(default=4000)),
            ],
            bases=("products.product",),
        ),
        migrations.CreateModel(
            name="Toy",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("age_range", models.CharField(max_length=80)),
                ("material", models.CharField(blank=True, max_length=120, null=True)),
                ("safety_standard", models.CharField(blank=True, max_length=120, null=True)),
            ],
            bases=("products.product",),
        ),
        migrations.CreateModel(
            name="Tablet",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("os", models.CharField(max_length=80)),
                ("screen_size_inch", models.DecimalField(decimal_places=1, default=10, max_digits=4)),
                ("storage_gb", models.PositiveIntegerField(default=128)),
                ("supports_pen", models.BooleanField(default=False)),
            ],
            bases=("products.product",),
        ),
        migrations.CreateModel(
            name="Headphones",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("connection_type", models.CharField(default="Bluetooth", max_length=80)),
                ("noise_cancelling", models.BooleanField(default=False)),
                ("battery_hours", models.PositiveIntegerField(default=0)),
            ],
            bases=("products.product",),
        ),
        migrations.CreateModel(
            name="Camera",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("sensor_type", models.CharField(max_length=120)),
                ("megapixels", models.DecimalField(decimal_places=1, max_digits=5)),
                ("lens_mount", models.CharField(blank=True, max_length=120, null=True)),
                ("video_resolution", models.CharField(blank=True, max_length=80, null=True)),
            ],
            bases=("products.product",),
        ),
        migrations.CreateModel(
            name="SmartWatch",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("os", models.CharField(max_length=80)),
                ("battery_days", models.PositiveIntegerField(default=1)),
                ("water_resistant", models.BooleanField(default=False)),
                ("health_features", models.CharField(blank=True, max_length=255, null=True)),
            ],
            bases=("products.product",),
        ),
        migrations.CreateModel(
            name="HomeAppliance",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("appliance_type", models.CharField(max_length=120)),
                ("power_watts", models.PositiveIntegerField(default=0)),
                ("capacity", models.CharField(blank=True, max_length=120, null=True)),
                ("energy_rating", models.CharField(blank=True, max_length=40, null=True)),
            ],
            bases=("products.product",),
        ),
        migrations.CreateModel(
            name="Clothing",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="products.product",
                    ),
                ),
                ("size", models.CharField(max_length=40)),
                ("color", models.CharField(max_length=80)),
                ("material", models.CharField(blank=True, max_length=120, null=True)),
                ("gender", models.CharField(blank=True, max_length=40, null=True)),
            ],
            bases=("products.product",),
        ),
    ]
