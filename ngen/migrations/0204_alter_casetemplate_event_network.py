# Generated by Django 4.0.5 on 2022-06-05 02:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0203_rename_state_casetemplate_case_state_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casetemplate',
            name='event_network',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.network'),
        ),
    ]
