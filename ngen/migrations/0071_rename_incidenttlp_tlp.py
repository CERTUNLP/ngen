# Generated by Django 4.0.1 on 2022-01-10 00:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0070_rename_incidentfeed_feed_alter_feed_table'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='IncidentTlp',
            new_name='Tlp',
        ),
    ]
