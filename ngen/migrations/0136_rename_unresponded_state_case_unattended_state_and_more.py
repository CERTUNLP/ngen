# Generated by Django 4.0.3 on 2022-03-30 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ngen', '0135_alter_case_unresponded_state_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='case',
            old_name='unresponded_state',
            new_name='unattended_state',
        ),
        migrations.RenameField(
            model_name='casetemplate',
            old_name='unresponded_state',
            new_name='unattended_state',
        ),
    ]
