# Generated by Django 4.0.4 on 2022-04-19 18:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0170_alter_eventtask_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='TodoTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('completed', models.BooleanField(default=False)),
                ('completed_date', models.DateTimeField(null=True)),
                ('note', models.TextField(null=True)),
                ('assigned_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'todo_task',
                'ordering': ['task__task_list'],
            },
        ),
        migrations.RenameField(
            model_name='task',
            old_name='title',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='event',
            name='tasks',
            field=models.ManyToManyField(related_name='events', through='ngen.TodoTask', to='ngen.task'),
        ),
        migrations.DeleteModel(
            name='EventTask',
        ),
        migrations.AddField(
            model_name='todotask',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todo_tasks', to='ngen.event'),
        ),
        migrations.AddField(
            model_name='todotask',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todo_tasks', to='ngen.task'),
        ),
        migrations.AlterUniqueTogether(
            name='todotask',
            unique_together={('task', 'event')},
        ),
    ]
