# Generated by Django 4.2.7 on 2024-11-18 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0014_alter_communicationchannel_additional_contacts'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailmessage',
            name='attachments',
            field=models.JSONField(blank=True, default=list),
        ),
    ]