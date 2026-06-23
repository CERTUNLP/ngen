from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ngen", "0033_view_about_page_permission"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="date",
            field=models.DateTimeField(
                blank=True,
                default=None,
                null=True,
            ),
        ),
    ]
