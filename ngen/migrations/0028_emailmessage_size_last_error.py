# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ngen", "0027_emailmessage_dispatched"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailmessage",
            name="size",
            field=models.PositiveIntegerField(
                null=True,
                help_text="Estimated size of the email message in bytes",
            ),
        ),
        migrations.AddField(
            model_name="emailmessage",
            name="last_error",
            field=models.TextField(
                null=True,
                blank=True,
                help_text="Last error message if sending failed",
            ),
        ),
    ]
