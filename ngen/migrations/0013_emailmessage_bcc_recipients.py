# Generated by Django 4.2.7 on 2024-11-10 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0012_emailmessage_template_params'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailmessage',
            name='bcc_recipients',
            field=models.JSONField(default=list),
        ),
    ]