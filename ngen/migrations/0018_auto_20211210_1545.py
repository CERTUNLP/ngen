# Generated by Django 3.2.5 on 2021-12-10 15:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ngen', '0017_remove_taxonomy_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxonomy',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
        migrations.AlterField(
            model_name='taxonomy',
            name='auto_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),

    ]
