# Generated by Django 4.1.10 on 2024-07-11 19:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ngen", "0004_artifactrelation_auto_created_alter_case_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="network",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="ngen.network",
            ),
        ),
    ]
