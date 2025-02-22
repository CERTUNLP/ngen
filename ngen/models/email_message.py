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
    EmailMessage model
    """

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
    template_params = models.JSONField(null=True)
    attachments = models.JSONField(default=list, blank=True)
    sent = models.BooleanField(default=False)
    send_attempt_failed = models.BooleanField(default=False)

    class Meta:
        db_table = "email_message"

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
