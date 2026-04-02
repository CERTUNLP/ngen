from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ngen", "0026_analyzer_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="analyzermapping",
            name="analyzer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="mappings",
                to="ngen.analyzer",
            ),
        ),
        migrations.RemoveField(
            model_name="analyzermapping",
            name="analyzer_type",
        ),
    ]
