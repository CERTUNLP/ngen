# Generated by Django 4.2.7 on 2024-11-10 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0013_emailmessage_bcc_recipients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communicationchannel',
            name='additional_contacts',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
