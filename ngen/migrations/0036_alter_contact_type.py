# Generated by Django 3.2.5 on 2021-12-15 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0035_alter_report_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='type',
            field=models.CharField(choices=[('email', 'email'), ('telegram', 'telegram'), ('phone', 'phone'), ('uri', 'uri')], default='email', max_length=20),
        ),
    ]