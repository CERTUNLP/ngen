"""
EmailMessage model
"""

from django.db import models

from ngen.models.common.mixins import AuditModelMixin


class EmailMessage(AuditModelMixin):
    """
    EmailMessage model
    """

    root_message_id = models.CharField(max_length=255)
    parent_message_id = models.CharField(blank=True, max_length=255)
    message_id = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255)
    date = models.DateTimeField()
    body = models.TextField()

    class Meta:
        db_table = "email_message"

    @classmethod
    def get_message_thread_by(cls, root_message_id):
        """
        Get all messages of a given root message id
        """
        return cls.objects.filter(root_message_id=root_message_id).order_by("date")
