# Generated by Django 4.0.1 on 2022-01-10 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0089_alter_case_feed_alter_case_tlp_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='active',
        ),
        migrations.RemoveField(
            model_name='case',
            name='deletedat',
        ),
        migrations.RemoveField(
            model_name='case',
            name='renotification_date',
        ),
        migrations.RemoveField(
            model_name='case',
            name='slug',
        ),
        migrations.AlterField(
            model_name='case',
            name='assigned',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='incidents_assigned', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='incidents_createdby', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='case',
            name='network',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.network'),
        ),
        migrations.AlterField(
            model_name='case',
            name='priority',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.priority'),
        ),
        migrations.AlterField(
            model_name='case',
            name='reporter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='incidents_reporter', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='case',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='incidents', to='ngen.state'),
        ),
        migrations.AlterField(
            model_name='case',
            name='taxonomy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.taxonomy'),
        ),
        migrations.AlterField(
            model_name='case',
            name='unresponded_state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='incidents_unresponded', to='ngen.state'),
        ),
        migrations.AlterField(
            model_name='case',
            name='unsolved_state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='incidents_unsolved', to='ngen.state'),
        ),
    ]
