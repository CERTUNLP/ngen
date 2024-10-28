"""
EmailMessage model
"""

from email.utils import make_msgid
from django.db import models
from ngen.models.common.mixins import AuditModelMixin


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
    subject = models.CharField(max_length=255)
    date = models.DateTimeField(null=True)
    body = models.TextField(null=True)
    template = models.CharField(max_length=255, null=True)
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
