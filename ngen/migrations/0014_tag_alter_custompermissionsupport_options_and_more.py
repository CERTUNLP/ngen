# Generated by Django 4.2.16 on 2024-12-05 13:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ngen', '0013_eventanalysis_analyzermapping'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('slug', models.SlugField(allow_unicode=True, max_length=100, unique=True, verbose_name='slug')),
                ('color', models.CharField(default='#007bff', max_length=7, validators=[django.core.validators.RegexValidator(message='Color must be a valid hexadecimal code (e.g. #007bff)', regex='^#[0-9A-Fa-f]{6}$')])),
            ],
            options={
                'verbose_name': 'CustomTag',
                'verbose_name_plural': 'CustomTags',
            },
        ),
        migrations.AlterModelOptions(
            name='custompermissionsupport',
            options={'default_permissions': (), 'managed': False, 'permissions': (('view_dashboard', 'View Dashboard'), ('view_minified_feed', 'View Minified Feed'), ('view_minified_tlp', 'View Minified TLP'), ('view_minified_priority', 'View Minified Priority'), ('view_minified_artifact', 'View Minified Artifact'), ('view_minified_user', 'View Minified User'), ('view_minified_case', 'View Minified Case'), ('view_minified_entity', 'View Minified Entity'), ('view_minified_contact', 'View Minified Contact'), ('view_minified_state', 'View Minified State'), ('view_minified_taxonomy', 'View Minified Taxonomy'), ('view_minified_taxonomygroup', 'View Minified TaxonomyGroup'), ('view_minified_permission', 'View Minified Permission'), ('view_minified_group', 'View Minified Group'), ('view_minified_tag', 'View Minified Tag'), ('view_userprofile', 'View UserProfile'), ('change_userprofile', 'Change UserProfile'), ('view_stringidentifier', 'View StringIdentifier'), ('use_stringidentifier', 'Use StringIdentifier'), ('view_dashboard_network_admin', 'View Dashboard as network admin'))},
        ),
        migrations.CreateModel(
            name='TaggedObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(db_index=True, verbose_name='object ID')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_tagged_items', to='contenttypes.contenttype', verbose_name='content type')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_items', to='ngen.tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='case',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='ngen.TaggedObject', to='ngen.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='event',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='ngen.TaggedObject', to='ngen.Tag', verbose_name='Tags'),
        ),
    ]
