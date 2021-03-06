# Generated by Django 4.0 on 2021-12-24 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0059_alter_incidentstate_slug_alter_statebehavior_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='networkentity',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='taxonomy',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
