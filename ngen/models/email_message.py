"""
EmailMessage model
"""

import hashlib
import re
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

    # RFC 5322 allows Message-IDs up to the 998-char line limit. 255 was a
    # latent batch-killer (a legit long id raised DataError on bulk_create) and
    # forced lossy truncation that could collide distinct ids during dedup.
    root_message_id = models.CharField(max_length=998)
    parent_message_id = models.CharField(null=True, max_length=998)
    message_id = models.CharField(max_length=998)
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

    # A path component must stay within the typical 255-byte filesystem limit.
    _MAX_DIR_KEY = 200
    _SAFE_DIR_KEY = re.compile(r"[A-Za-z0-9._@<>+=-]+")

    def _attachment_dir_key(self):
        """
        Bounded, filesystem-safe directory key for this message's attachments.

        A Message-ID can legally reach the RFC 5322 998-char line limit and may
        carry characters that are awkward as a path component; either can exceed
        the ~255-byte filesystem limit (ENAMETOOLONG) and make the attachment
        write fail. A short, already-safe id is used verbatim (so existing paths
        stay valid); anything longer or unsafe falls back to a stable hash.
        """
        key = self.message_id or (str(self.id) if self.id else "")
        if key and len(key) <= self._MAX_DIR_KEY and self._SAFE_DIR_KEY.fullmatch(key):
            return key
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def attachment_path(self, filename):
        """
        Return the relative path for an email attachment
        """
        attachments_path = path.join(
            settings.EMAIL_ATTACHMENTS_FILE_ROOT,
            self._attachment_dir_key(),
            filename,
        )

        return attachments_path
