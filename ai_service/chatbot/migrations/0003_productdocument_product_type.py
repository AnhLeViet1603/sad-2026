from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chatbot", "0002_productdocument_vector"),
    ]

    operations = [
        migrations.AddField(
            model_name="productdocument",
            name="product_type",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name="productdocument",
            name="type_details",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
