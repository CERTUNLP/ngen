# Generated by Django 4.0.1 on 2022-02-09 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0121_alter_event_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='network',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='events', to='ngen.network'),
        ),
    ]