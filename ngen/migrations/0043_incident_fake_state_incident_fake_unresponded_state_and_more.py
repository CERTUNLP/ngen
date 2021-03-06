# Generated by Django 4.0 on 2021-12-24 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0042_auto_20211224_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='fake_state',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='incident',
            name='fake_unresponded_state',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='incident',
            name='fake_unsolved_state',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='incidentdecision',
            name='fake_state',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='incidentdecision',
            name='fake_unresponded_state',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='incidentdecision',
            name='fake_unsolved_state',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='incidentdetected',
            name='fake_state',
            field=models.IntegerField(null=True),
        ),
    ]
