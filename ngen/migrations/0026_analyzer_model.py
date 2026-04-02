from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("ngen", "0023_alter_casetemplate_case_tlp_and_more_squashed_0025_remove_casetemplate_priority_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Analyzer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name="created")),
                ("modified", model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name="modified")),
                ("name", models.CharField(max_length=255, unique=True)),
                ("type", models.CharField(max_length=50)),
                ("enabled", models.BooleanField(default=True)),
                ("config", models.JSONField(default=dict)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "db_table": "analyzer",
            },
        ),
    ]
