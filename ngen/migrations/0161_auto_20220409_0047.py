# Generated by Django 4.0.3 on 2022-04-09 00:47

from django.db import migrations


def remove_undefined_priority(apps, schema_editor):
    State = apps.get_model('ngen', 'State')
    State.objects.filter(name='Unresolved').delete()
    undefined = State.objects.filter(name='Undefined').first()
    if undefined:
        undefined.cases.update(state=State.objects.get(name='Staging'))
        undefined.decision_states.update(state=State.objects.get(name='Staging'))
        undefined.delete()

    # removed = State.objects.get(name='Removed')
    # if removed:
    #     for case in removed.cases.all():
    #         case.delete()
    #     removed.delete()

    for discarded in State.objects.filter(name__startswith='Discarded by'):
        discarded.cases.update(state=State.objects.get(name='Closed'))
        discarded.decision_states.update(state=State.objects.get(name='Closed'))
        discarded.delete()

    for closed in State.objects.filter(name__startswith='Closed by'):
        closed.cases.update(state=State.objects.get(name='Closed'))
        closed.decision_states.update(state=State.objects.get(name='Closed'))
        closed.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('ngen', '0160_remove_case_created_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casetemplate',
            name='unattended_state',
        ),
        migrations.RemoveField(
            model_name='casetemplate',
            name='unsolved_state',
        ),
        migrations.DeleteModel(
            name='IncidentStateChange',
        ),
        migrations.RunPython(remove_undefined_priority)
    ]
