# Generated by Django 4.2.16 on 2024-10-24 12:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0014_ngentag_taggedobject_alter_case_tags_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='NgenTag',
            new_name='Tag',
        ),
    ]
