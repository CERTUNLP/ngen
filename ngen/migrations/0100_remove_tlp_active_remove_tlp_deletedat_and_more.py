# Generated by Django 4.0.1 on 2022-01-10 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0099_remove_priority_deletedat_alter_priority_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tlp',
            name='active',
        ),
        migrations.RemoveField(
            model_name='tlp',
            name='deletedat',
        ),
        migrations.AlterField(
            model_name='tlp',
            name='code',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='created_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ngen.user'),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='description',
            field=models.TextField(max_length=150),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='encrypt',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='information',
            field=models.TextField(max_length=10),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='name',
            field=models.CharField(max_length=45),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='rgb',
            field=models.CharField(max_length=45),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='updated_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='when',
            field=models.TextField(max_length=500),
        ),
        migrations.AlterField(
            model_name='tlp',
            name='why',
            field=models.TextField(max_length=500),
        ),
        migrations.AlterModelTable(
            name='tlp',
            table='tlp',
        ),
    ]
