# Generated by Django 4.0.3 on 2022-03-16 21:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0128_auto_20220315_2318'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='ngen.case'),
        ),
    ]
