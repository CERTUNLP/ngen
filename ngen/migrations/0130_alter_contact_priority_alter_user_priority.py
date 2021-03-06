# Generated by Django 4.0.3 on 2022-03-24 00:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0129_case_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='priority',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.priority'),
        ),
        migrations.AlterField(
            model_name='user',
            name='priority',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.priority'),
        ),
    ]
