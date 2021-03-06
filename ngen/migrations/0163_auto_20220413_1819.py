# Generated by Django 4.0.3 on 2022-04-13 18:19
import json

from auditlog.models import LogEntry
from django.db import migrations


def log_create(case, changes: dict, date):
    logentry = LogEntry.objects.log_create(case, action=LogEntry.Action.UPDATE, changes=json.dumps(changes))
    logentry.timestamp = date
    logentry.object_repr = str(case.id)
    logentry.save()


def empty_state_change_to_logentry(apps, schema_editor):
    Case = apps.get_model('ngen', 'Case')
    for case in Case.objects.all():
        if not case.history.all():
            log_create(case, {'state': ('Initial', 'Staging')}, case.created)
            log_create(case, {'state': ('Staging', case.state.name)}, case.modified)


class Migration(migrations.Migration):
    dependencies = [
        ('ngen', '0162_auto_20220409_0130'),
    ]

    operations = [
        migrations.RunPython(empty_state_change_to_logentry)

    ]
