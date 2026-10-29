from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Widen EmailMessage id/threading fields from 255 to 998 chars (RFC 5322 line
    limit). At 255 a legitimately long Message-ID raised DataError and aborted
    the whole bulk_create batch, and truncating to fit could collide distinct
    ids during de-duplication. Plain column widening: no data loss, no new
    constraint.
    """

    dependencies = [
        ("ngen", "0038_user_email_unique"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailmessage",
            name="root_message_id",
            field=models.CharField(max_length=998),
        ),
        migrations.AlterField(
            model_name="emailmessage",
            name="parent_message_id",
            field=models.CharField(max_length=998, null=True),
        ),
        migrations.AlterField(
            model_name="emailmessage",
            name="message_id",
            field=models.CharField(max_length=998),
        ),
    ]
