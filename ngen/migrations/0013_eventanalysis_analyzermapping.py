# Generated by Django 4.2.16 on 2024-12-05 12:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0012_alter_custompermissionsupport_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('analyzer_type', models.CharField(max_length=255)),
                ('vulnerable', models.BooleanField()),
                ('result', models.TextField()),
                ('target', models.CharField(max_length=255)),
                ('scan_type', models.CharField(max_length=255)),
                ('analyzer_url', models.CharField(max_length=255)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analyses', to='ngen.event')),
            ],
            options={
                'db_table': 'event_analysis',
            },
        ),
        migrations.CreateModel(
            name='AnalyzerMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('mapping_to', models.CharField(max_length=255)),
                ('analyzer_type', models.CharField(max_length=255)),
                ('mapping_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mappings', to='ngen.taxonomy')),
            ],
            options={
                'db_table': 'analyzer_mapping',
            },
        ),
    ]