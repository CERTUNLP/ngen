from django.db import migrations, models
import django.db.models.deletion


def delete_orphaned_mappings(apps, schema_editor):
    AnalyzerMapping = apps.get_model("ngen", "AnalyzerMapping")
    AnalyzerMapping.objects.filter(analyzer__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ngen", "0025_analyzermapping_add_analyzer_fk"),
    ]

    operations = [
        migrations.RunPython(delete_orphaned_mappings, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="analyzermapping",
            name="analyzer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mappings",
                to="ngen.analyzer",
            ),
        ),
    ]