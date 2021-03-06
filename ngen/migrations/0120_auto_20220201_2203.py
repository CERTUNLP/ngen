# Generated by Django 4.0.1 on 2022-02-01 22:03

from django.db import migrations


def replace_report_strings(apps, schema_editor):
    reports = apps.get_model('ngen', 'Report')
    for report in reports.objects.all():
        report.problem = report.problem.replace('incident.hostAddress', 'event.network')
        if report.derived_problem:
            report.derived_problem = report.derived_problem.replace('incident.hostAddress', 'event.network')
        if report.verification:
            report.verification = report.verification.replace('incident.hostAddress', 'event.network')
        if report.recommendations:
            report.recommendations = report.recommendations.replace('incident.hostAddress', 'event.network')
        if report.more_information:
            report.more_information = report.more_information.replace('incident.hostAddress', 'event.network')
        report.save()


class Migration(migrations.Migration):
    dependencies = [
        ('ngen', '0119_alter_priority_options_alter_report_derived_problem_and_more'),
    ]

    operations = [
        migrations.RunPython(
            code=replace_report_strings,
        ),
    ]
