# Generated by Django 4.0.4 on 2022-04-19 19:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0173_alter_todotask_options_playbook_alter_task_task_list_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='task_list',
            new_name='playbook',
        ),
    ]
