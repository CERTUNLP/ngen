# Generated by Django 4.0.1 on 2022-01-18 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0111_alter_feed_slug_alter_tlp_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='case',
            options={'ordering': ['-id']},
        ),
        migrations.AlterField(
            model_name='event',
            name='case',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='ngen.case'),
        ),
    ]
