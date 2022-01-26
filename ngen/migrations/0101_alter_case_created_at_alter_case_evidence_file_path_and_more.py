# Generated by Django 4.0.1 on 2022-01-10 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0100_remove_tlp_active_remove_tlp_deletedat_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='created_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='case',
            name='evidence_file_path',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='notes',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='raw',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='report_message_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='response_dead_line',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='solve_dead_line',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='updated_at',
            field=models.DateTimeField(),
        ),
    ]