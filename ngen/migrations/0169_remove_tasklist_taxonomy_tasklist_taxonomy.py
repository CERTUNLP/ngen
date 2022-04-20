# Generated by Django 4.0.4 on 2022-04-18 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0168_event_tasks_alter_eventtask_event_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tasklist',
            name='taxonomy',
        ),
        migrations.AddField(
            model_name='tasklist',
            name='taxonomy',
            field=models.ManyToManyField(related_name='task_lists', to='ngen.taxonomy'),
        ),
    ]
