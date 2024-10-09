# Generated by Django 4.2.15 on 2024-10-08 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0011_alter_case_options_alter_contact_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='custompermissionsupport',
            options={'default_permissions': (), 'managed': False, 'permissions': (('view_dashboard', 'View Dashboard'), ('view_minified_feed', 'View Minified Feed'), ('view_minified_tlp', 'View Minified TLP'), ('view_minified_priority', 'View Minified Priority'), ('view_minified_artifact', 'View Minified Artifact'), ('view_minified_user', 'View Minified User'), ('view_minified_case', 'View Minified Case'), ('view_minified_entity', 'View Minified Entity'), ('view_minified_contact', 'View Minified Contact'), ('view_minified_state', 'View Minified State'), ('view_minified_taxonomy', 'View Minified Taxonomy'), ('view_minified_taxonomygroup', 'View Minified TaxonomyGroup'), ('view_minified_permission', 'View Minified Permission'), ('view_minified_group', 'View Minified Group'), ('view_userprofile', 'View UserProfile'), ('change_userprofile', 'Change UserProfile'), ('view_stringidentifier', 'View StringIdentifier'), ('use_stringidentifier', 'Use StringIdentifier'), ('view_dashboard_network_admin', 'View Dashboard as network admin'))},
        ),
        migrations.AlterField(
            model_name='network',
            name='contacts',
            field=models.ManyToManyField(blank=True, related_name='networks', to='ngen.contact'),
        ),
    ]