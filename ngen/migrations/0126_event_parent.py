# Generated by Django 4.0.3 on 2022-03-15 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0125_alter_caseevidence_file_alter_eventevidence_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.event'),
        ),
    ]
