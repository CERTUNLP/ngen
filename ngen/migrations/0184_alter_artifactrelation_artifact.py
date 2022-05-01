# Generated by Django 4.0.4 on 2022-05-01 20:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0183_alter_artifactrelation_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artifactrelation',
            name='artifact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artifact_relation', to='ngen.artifact'),
        ),
    ]