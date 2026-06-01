from django.db import migrations, models
import pgvector.django


class Migration(migrations.Migration):
    dependencies = [
        ("chatbot", "0001_initial"),
    ]

    operations = [
        pgvector.django.VectorExtension(),
        migrations.AddField(
            model_name="productdocument",
            name="document",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="productdocument",
            name="embedding",
            field=pgvector.django.VectorField(blank=True, dimensions=3072, null=True),
        ),
    ]

