# Generated by Django 4.1.10 on 2024-05-09 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ngen", "0002_evidence_assigned_name_evidence_extension_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="evidence",
            name="original_filename",
            field=models.CharField(
                blank=True, default="", editable=False, max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="evidence",
            name="assigned_name",
            field=models.CharField(blank=True, default="", max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="evidence",
            name="extension",
            field=models.CharField(
                blank=True, default="", editable=False, max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="evidence",
            name="mime",
            field=models.CharField(
                blank=True, default="", editable=False, max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="evidence",
            name="size",
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]
