# Generated by Django 4.0.4 on 2022-05-01 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0180_alter_artifactrelation_content_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artifact',
            name='value',
            field=models.CharField(max_length=255),
        ),
    ]
