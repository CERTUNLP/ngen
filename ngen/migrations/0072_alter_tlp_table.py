# Generated by Django 4.0.1 on 2022-01-10 00:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0071_rename_incidenttlp_tlp'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='tlp',
            table='lp',
        ),
    ]
