# Generated by Django 4.0.4 on 2022-05-01 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0181_alter_artifact_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artifact',
            name='value',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
