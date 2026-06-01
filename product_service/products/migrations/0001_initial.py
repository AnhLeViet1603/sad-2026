from django.db import migrations, models
import django.db.models.deletion
import pgvector.django


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        pgvector.django.VectorExtension(),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(unique=True)),
                ("parent_id", models.BigIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="ProductAttribute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("code", models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "status",
                    models.CharField(
                        choices=[("ACTIVE", "Active"), ("INACTIVE", "Inactive"), ("OUT_OF_STOCK", "Out of stock")],
                        default="ACTIVE",
                        max_length=30,
                    ),
                ),
                ("brand", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="products.category",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image_url", models.URLField()),
                ("alt_text", models.CharField(blank=True, max_length=255, null=True)),
                ("is_primary", models.BooleanField(default=False)),
                (
                    "product",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="products.product"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Inventory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=0)),
                ("reserved_quantity", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="inventory", to="products.product"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductAttributeValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.CharField(max_length=255)),
                (
                    "attribute",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="products.productattribute"),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attribute_values",
                        to="products.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductEmbedding",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("document", models.TextField()),
                ("embedding", pgvector.django.VectorField(blank=True, dimensions=384, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="embedding", to="products.product"),
                ),
            ],
        ),
    ]

