# Generated by Django 4.0.1 on 2022-01-11 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0106_event_network'),
    ]

    operations = [
        migrations.AlterField(
            model_name='behavior',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='casetemplate',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='edge',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='event',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='feed',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='network',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='networkentity',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='priority',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='report',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='state',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='taxonomy',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ngen.user'),
        ),
    ]
