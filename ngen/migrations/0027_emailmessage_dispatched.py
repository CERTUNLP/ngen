# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ngen", "0026_analyzermapping_cascade_analyzer"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailmessage",
            name="dispatched",
            field=models.BooleanField(
                default=False,
                help_text="True if async_send_email.delay() was called. False means stored for manual sending.",
            ),
        ),
        migrations.AlterModelOptions(
            name="emailmessage",
            options={"ordering": ["-created"]},
        ),
    ]
