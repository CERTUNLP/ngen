# Generated by Django 3.2.5 on 2021-12-04 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0022_priority_repited_deletion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incidenturgency',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='incidentpriority',
            name='impact',
        ),
        migrations.RemoveField(
            model_name='incidentpriority',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='incidentpriority',
            name='urgency',
        ),
        migrations.DeleteModel(
            name='IncidentImpact',
        ),
        migrations.DeleteModel(
            name='IncidentUrgency',
        ),
    ]
