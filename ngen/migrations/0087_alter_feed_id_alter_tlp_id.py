# Generated by Django 4.0.1 on 2022-01-10 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0086_rename_fake_id_feed_id_rename_fake_id_tlp_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
