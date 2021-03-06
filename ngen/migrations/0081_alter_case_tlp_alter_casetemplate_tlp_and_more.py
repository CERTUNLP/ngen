# Generated by Django 4.0.1 on 2022-01-10 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0080_case_fake_feed_case_fake_tlp_casetemplate_fake_feed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='tlp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.tlp'),
        ),
        migrations.AlterField(
            model_name='casetemplate',
            name='tlp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.tlp'),
        ),
        migrations.AlterField(
            model_name='event',
            name='tlp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.tlp'),
        ),
    ]
