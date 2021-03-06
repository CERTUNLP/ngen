# Generated by Django 4.0.5 on 2022-06-05 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0202_remove_incidentcommentthread_case_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='casetemplate',
            old_name='state',
            new_name='case_state',
        ),
        migrations.RenameField(
            model_name='casetemplate',
            old_name='tlp',
            new_name='case_tlp',
        ),
        migrations.RenameField(
            model_name='casetemplate',
            old_name='feed',
            new_name='event_feed',
        ),
        migrations.RenameField(
            model_name='casetemplate',
            old_name='network',
            new_name='event_network',
        ),
        migrations.RenameField(
            model_name='casetemplate',
            old_name='taxonomy',
            new_name='event_taxonomy',
        ),
        migrations.AddField(
            model_name='casetemplate',
            name='case_lifecycle',
            field=models.CharField(choices=[('manual', 'Manual'), ('auto', 'Auto'), ('auto_open', 'Auto open'), ('auto_close', 'Auto close')], default='auto', max_length=20),
        ),
        migrations.AddField(
            model_name='casetemplate',
            name='event_count',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
