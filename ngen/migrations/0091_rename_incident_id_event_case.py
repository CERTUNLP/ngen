# Generated by Django 4.0.1 on 2022-01-10 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0090_remove_case_active_remove_case_deletedat_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='incident_id',
            new_name='case',
        ),
    ]