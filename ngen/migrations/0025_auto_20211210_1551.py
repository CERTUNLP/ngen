# Generated by Django 3.2.5 on 2021-12-10 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0024_auto_20211210_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='taxonomy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.taxonomy'),
        ),
        migrations.AlterField(
            model_name='incidentdecision',
            name='taxonomy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.taxonomy'),
        ),
        migrations.AlterField(
            model_name='incidentdetected',
            name='taxonomy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.taxonomy'),
        ),
        migrations.AlterField(
            model_name='incidentreport',
            name='taxonomy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.taxonomy'),
        ),
    ]