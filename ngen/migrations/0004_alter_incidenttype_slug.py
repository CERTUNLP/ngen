# Generated by Django 3.2.5 on 2021-12-09 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0003_auto_20211209_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incidenttype',
            name='slug',
            field=models.SlugField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
