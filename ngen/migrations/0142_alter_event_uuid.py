# Generated by Django 4.0.3 on 2022-04-03 23:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0141_event_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]