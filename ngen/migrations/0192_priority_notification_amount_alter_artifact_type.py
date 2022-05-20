# Generated by Django 4.0.4 on 2022-05-20 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0191_case_notification_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='priority',
            name='notification_amount',
            field=models.PositiveSmallIntegerField(default=3),
        ),
        migrations.AlterField(
            model_name='artifact',
            name='type',
            field=models.CharField(choices=[('ip', 'IP'), ('domain', 'Domain'), ('fqdn', 'FQDN'), ('url', 'Url'), ('mail', 'Mail'), ('hash', 'Hash'), ('file', 'File'), ('other', 'Other'), ('user-agent', 'User agent'), ('autonomous-system', 'Autonomous system')], default='ip', max_length=20),
        ),
    ]
