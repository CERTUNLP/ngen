# Generated by Django 4.0.1 on 2022-01-10 17:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ngen', '0093_remove_event_active_remove_event_deletedat_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='priority',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.priority'),
        ),
        migrations.AlterField(
            model_name='event',
            name='taxonomy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.taxonomy'),
        )
    ]
