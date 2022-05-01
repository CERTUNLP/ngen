# Generated by Django 4.0.4 on 2022-04-17 19:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ngen', '0164_auto_20220413_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='lifecycle',
            field=models.CharField(choices=[('manual', 'manual'), ('auto', 'auto'), ('auto_open', 'auto_open'),
                                            ('auto_close', 'auto-close')], default='manual', max_length=20),
        ),
    ]