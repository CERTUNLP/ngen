# Generated by Django 3.2.5 on 2021-12-10 14:49

from django.db import migrations, models


def add_auto_id(apps, schema_editor):
    taxonomies = apps.get_model('ngen', 'Taxonomy')
    for n, taxonomy in enumerate(taxonomies.objects.all()):
        taxonomy.auto_id = n
        taxonomy.save()


class Migration(migrations.Migration):
    dependencies = [
        ('ngen', '0011_auto_20211209_2357'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxonomy',
            name='auto_id',
            field=models.IntegerField(null=True),
        ),
        migrations.RunPython(
            code=add_auto_id,
        ),
    ]
