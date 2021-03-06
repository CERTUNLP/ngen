# Generated by Django 4.0.4 on 2022-05-27 19:58

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0193_activesession'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artifact',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='priority',
            name='color',
            field=colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=[('#FFFFFF', 'white'), ('#000000', 'black')]),
        ),
    ]
