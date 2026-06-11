# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ngen", "0028_emailmessage_size_last_error"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailmessage",
            name="retried",
            field=models.BooleanField(
                default=False,
                help_text="True if this failed email was already retried (cloned and dispatched)",
            ),
        ),
    ]
