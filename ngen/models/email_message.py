"""
EmailMessage model
"""

from os import path
from email.utils import make_msgid
from django.db import models
from ngen.models.common.mixins import AuditModelMixin
from django.conf import settings


class EmailMessage(AuditModelMixin):
    """
    EmailMessage model — persistence layer for all outgoing emails.
    Celery is the actual queue; EmailMessage is the audit log.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CANCELLED = "cancelled", "Cancelled"
        SENDING = "sending", "Sending"
        RETRYING = "retrying", "Retrying"
        FAILED = "failed", "Failed"
        SENT = "sent", "Sent"

    root_message_id = models.CharField(max_length=255)
    parent_message_id = models.CharField(null=True, max_length=255)
    message_id = models.CharField(max_length=255)
    references = models.JSONField(default=list)
    senders = models.JSONField(default=list)
    recipients = models.JSONField(default=list)
    bcc_recipients = models.JSONField(default=list)
    subject = models.CharField(max_length=255)
    date = models.DateTimeField(null=True)
    body = models.TextField(null=True)
    body_html = models.TextField(null=True)
    template = models.CharField(max_length=255, null=True)
    attachments = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    size = models.PositiveIntegerField(
        null=True,
        help_text="Estimated size of the email message in bytes",
    )
    last_error = models.TextField(
        null=True,
        blank=True,
        help_text="Last error message if sending failed",
    )
    retried = models.BooleanField(
        default=False,
        help_text="True if this failed email was already retried (cloned and dispatched)",
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of Celery retry attempts for this email",
    )

    class Meta:
        db_table = "email_message"
        ordering = ["-created"]

    @classmethod
    def generate_message_id(cls, domain: str):
        """
        Generate a message id
        """
        return make_msgid(domain=domain)

    @classmethod
    def get_message_thread_by(cls, root_message_id):
        """
        Get all messages of a given root message id
        """
        return cls.objects.filter(root_message_id=root_message_id).order_by("created")

    def attachment_path(self, filename):
        """
        Return the relative path for an email attachment
        """
        attachments_path = path.join(
            settings.EMAIL_ATTACHMENTS_FILE_ROOT,
            self.message_id or self.id,
            filename,
        )

        return attachments_path
