# Generated by Django 4.1.10 on 2024-08-05 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0006_taxonomygroup_event_initial_taxonomy_slug_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxonomy',
            name='needs_review',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='taxonomygroup',
            name='needs_review',
            field=models.BooleanField(default=True),
        ),
    ]