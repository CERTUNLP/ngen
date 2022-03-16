# Generated by Django 4.0.3 on 2022-03-15 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0126_event_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='ngen.event'),
        ),
        migrations.AlterField(
            model_name='network',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='ngen.network'),
        ),
        migrations.AlterField(
            model_name='taxonomy',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='ngen.taxonomy'),
        ),
    ]