# Generated by Django 4.0.1 on 2022-01-10 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0097_remove_casetemplate_auto_saved_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feed',
            name='deletedat',
        ),
        migrations.AlterField(
            model_name='feed',
            name='created_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='feed',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='feed',
            name='description',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='feed',
            name='updated_at',
            field=models.DateTimeField(),
        ),
    ]