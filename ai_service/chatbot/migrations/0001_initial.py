from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ChatSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.BigIntegerField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ProductDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_id", models.BigIntegerField(unique=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("category", models.CharField(blank=True, max_length=255, null=True)),
                ("brand", models.CharField(blank=True, max_length=255, null=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("stock", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="RecommendationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.BigIntegerField(blank=True, db_index=True, null=True)),
                ("query", models.TextField(blank=True, null=True)),
                ("product_ids", models.JSONField(default=list)),
                ("source", models.CharField(default="mock", max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="UserBehavior",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.BigIntegerField(db_index=True)),
                ("product_id", models.BigIntegerField(db_index=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("VIEWED", "Viewed"),
                            ("ADDED_TO_CART", "Added to cart"),
                            ("PURCHASED", "Purchased"),
                            ("RATED", "Rated"),
                        ],
                        max_length=30,
                    ),
                ),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ChatMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(max_length=20)),
                ("content", models.TextField()),
                ("products", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "session",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="chatbot.chatsession"),
                ),
            ],
        ),
    ]

