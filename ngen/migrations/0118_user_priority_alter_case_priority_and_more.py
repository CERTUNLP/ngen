# Generated by Django 4.0.1 on 2022-01-27 21:15

import django.db.models.deletion
from django.db import migrations, models


def add_default_priority(apps, schema_editor):
    users = apps.get_model('ngen', 'User')
    for user in users.objects.all():
        if not user.priority:
            user.priority = apps.get_model('ngen', 'Priority').default_priority()
        user.save()


class Migration(migrations.Migration):
    dependencies = [
        ('ngen', '0117_alter_user_managers_remove_user_created_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='priority',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.priority'),
        ),
        migrations.RunPython(
            code=add_default_priority,
        ),
    ]