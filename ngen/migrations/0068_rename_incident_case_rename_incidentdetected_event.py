# Generated by Django 4.0.1 on 2022-01-09 23:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0067_taxonomy_type_alter_report_lang'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Incident',
            new_name='Case',
        ),
        migrations.RenameModel(
            old_name='IncidentDetected',
            new_name='Event',
        ),
    ]
