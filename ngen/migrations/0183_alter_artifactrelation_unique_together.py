# Generated by Django 4.0.4 on 2022-05-01 02:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ngen', '0182_alter_artifact_value'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='artifactrelation',
            unique_together={('artifact', 'object_id', 'content_type')},
        ),
    ]
