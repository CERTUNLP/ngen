# Generated by Django 3.2.5 on 2021-11-29 22:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0018_auto_20211129_2203'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='network',
            options={'ordering': ['-cidr', 'domain']},
        ),
    ]