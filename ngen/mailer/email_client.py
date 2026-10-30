from os import makedirs, path
import email
import hashlib
import logging
from django.conf import settings
from email.message import Message
from typing import List
from imbox.messages import Messages
from ngen.mailer.email_protocol_strategy.email_protocol_strategy import (
    EmailProtocolStrategy,
)
from ngen.mailer.email_protocol_strategy.imap_strategy import IMAPStrategy
from ngen.models.email_message import EmailMessage

logger = logging.getLogger(__name__)


class EmailClient:
    """
    Email client class to fetch emails.
    Example usage:

    email_client = EmailClient(host="some.host", username="some_username", password="some_password")

    unread_emails = email_client.fetch_unread_emails()
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 993,
        ssl: bool = True,
        timeout: int = None,
        protocol: EmailProtocolStrategy = IMAPStrategy,
    ):

        self.protocol = protocol(
            host=host, username=username, password=password, port=port, ssl=ssl, timeout=timeout
        )

        self.login()

    def login(self):
        """
        Login to email server
        """
        if self.protocol:
            self.protocol.login()

    def logout(self):
        """
        Logout from email server
        """
        if self.protocol:
            self.protocol.logout()

    def fetch_emails(self, folder: str) -> list:
        """
        Fetch emails from a folder with a specific flag
        """
        return self.protocol.fetch_emails(folder)

    def fetch_all_emails(self) -> list:
        """
        Fetch all emails
        """
        return self.protocol.fetch_all_emails()

    def fetch_unread_emails(self) -> list:
        """
        Fetch unread emails
        """
        return self.protocol.fetch_unread_emails()

    def mark_emails_as_read(self, emails: list):
        """
        Mark emails as read
        """
        self.protocol.mark_emails_as_read(emails)

    # Helper methods

    def map_email(self, email: Messages) -> EmailMessage:
        """
        Map an imbox message (and its attachments) to an EmailMessage.

        Defensive by design: a malformed inbound message (missing Message-ID,
        Subject or Date header, or without a text/plain part) must never abort
        ingestion, and nothing is silently discarded. Plain text goes to
        ``body`` and HTML to ``body_html`` so no content is lost.
        """
        message_id = self.get_message_id(email)
        body, body_html = self._extract_body(email)
        subject = self._clean(getattr(email, "subject", "") or "")
        subject = subject.strip().replace("\r", "").replace("\n", "")

        email_message = EmailMessage(
            root_message_id=self._bound_id(self.get_root_message_id(email)) or message_id,
            parent_message_id=self._bound_id(self.get_parent_message_id(email)),
            references=self._clean(self.get_references_field(email)),
            message_id=message_id,
            senders=self._clean(getattr(email, "sent_from", None) or []),
            recipients=self._clean(getattr(email, "sent_to", None) or []),
            date=getattr(email, "parsed_date", None),
            subject=subject[:255],
            body=body,
            body_html=body_html,
            status=EmailMessage.Status.SENT,
        )

        # Defer attachment persistence until *after* de-duplication (see
        # persist_attachments / retrieve_emails): writing here, before the
        # duplicate check, let a discarded duplicate overwrite a retained
        # message's files (same Message-ID + filename), and touched the
        # filesystem for records we were about to throw away. We only carry the
        # raw imbox attachments forward on the instance for now.
        email_message._pending_attachments = getattr(email, "attachments", None) or []

        return email_message

    def persist_attachments(self, email_message: EmailMessage) -> EmailMessage:
        """
        Write the attachments deferred by :meth:`map_email` to MEDIA_ROOT and
        fill ``email_message.attachments`` with their metadata.

        Called only for the records we are actually going to store (after
        de-duplication). A single unwritable attachment is never fatal and never
        silently lost: the parsed message is kept and the failure is recorded in
        ``last_error`` so it stays visible and queryable for later recovery
        (the message is marked read, so it will not be re-fetched).
        """
        attachments = []
        errors = []

        for attachment in getattr(email_message, "_pending_attachments", None) or []:
            filename = attachment.get("filename")
            content = attachment.get("content")

            if not filename or not content:
                continue

            try:
                # The filename comes from the sender: keep only its last path
                # component so it is always stored inside this message's
                # attachment directory.
                safe_name = path.basename(str(filename).replace("\\", "/"))
                if safe_name in ("", ".", ".."):
                    raise ValueError("unusable attachment filename")

                attachment_path = email_message.attachment_path(safe_name)
                download_path = path.join(settings.MEDIA_ROOT, attachment_path)

                makedirs(path.dirname(download_path), exist_ok=True)
                with open(download_path, "wb") as file:
                    file.write(content.read())

                attachments.append({"name": filename, "file": attachment_path})
            except (OSError, ValueError) as e:
                # Drop only this attachment (ValueError covers e.g. a NUL in the
                # decoded filename), keep the parsed message, but leave a durable
                # trace so the loss is never silent. repr() escapes control
                # chars so the diagnostic itself is storable.
                logger.warning("Failed to save attachment %r: %s", filename, e)
                errors.append("%r: %s" % (filename, e))

        email_message.attachments = attachments
        if errors:
            note = self._clean("attachment storage failed -> %s" % "; ".join(errors))
            email_message.last_error = (
                "%s\n%s" % (email_message.last_error, note)
                if email_message.last_error
                else note
            )[:2000]

        return email_message

    @classmethod
    def _clean(cls, value):
        """
        Replace NUL characters, recursively through lists/dicts. PostgreSQL
        cannot store NUL in text or jsonb columns, so a single malformed part
        would otherwise make bulk_create fail and stall the whole batch.
        """
        if isinstance(value, str):
            return value.replace("\x00", "�")
        if isinstance(value, list):
            return [cls._clean(v) for v in value]
        if isinstance(value, dict):
            return {cls._clean(k): cls._clean(v) for k, v in value.items()}
        return value

    @staticmethod
    def _bound_id(value):
        """
        Keep a Message-ID-like value within the 998-char column. A folded header
        can exceed it (DataError on insert); fall back to a stable hash so the
        value stays deterministic for de-duplication.
        """
        if not value:
            return value
        value = EmailClient._clean(value)
        if len(value) <= 998:
            return value
        digest = hashlib.sha256(value.encode("utf-8", "surrogatepass")).hexdigest()
        return "<%s@long-message-id.ngen>" % digest

    @classmethod
    def _as_text(cls, value) -> str:
        """Coerce an imbox body part (str or bytes) to storable text."""
        if isinstance(value, bytes):
            value = value.decode("utf-8", "replace")
        return cls._clean(value or "")

    def _extract_body(self, email: Messages):
        """
        Return ``(plain_text, html)`` from an imbox message, tolerating a
        message that only has one of the two parts (or neither).
        """
        body = getattr(email, "body", None) or {}
        plain = body.get("plain") or []
        html = body.get("html") or []
        # Keep every part of each type (a multipart may carry several), joined in
        # order, so nothing is silently dropped.
        return (
            "\n".join(self._as_text(p) for p in plain),
            "\n".join(self._as_text(h) for h in html),
        )

    def build_error_message(self, email: Messages, error: Exception) -> EmailMessage:
        """
        Build a viewable placeholder EmailMessage for an inbound message that
        could not be parsed, so the conversation still shows that something
        arrived and the failure is recorded (``last_error``) instead of
        crashing the whole batch.
        """
        try:
            message_id = self.get_message_id(email)
        except Exception:  # pragma: no cover - last-resort safety net
            message_id = EmailMessage.generate_message_id(domain="no-message-id.ngen")

        # Recover threading headers best-effort so the placeholder still threads
        # into the case conversation (CommunicationChannel.get_messages filters
        # by root_message_id); fall back to its own id only if unrecoverable.
        try:
            references = self._clean(self.get_references_field(email))
        except Exception:
            references = []
        try:
            parent_message_id = self._bound_id(self.get_parent_message_id(email))
        except Exception:
            parent_message_id = None
        root_message_id = self._bound_id(references[0] if references else None) or message_id

        try:
            subject = self._clean(getattr(email, "subject", "") or "")[:255]
        except Exception:  # pragma: no cover - last-resort safety net
            subject = ""

        return EmailMessage(
            root_message_id=root_message_id,
            parent_message_id=parent_message_id,
            references=references,
            message_id=message_id,
            senders=self._clean(getattr(email, "sent_from", None) or []),
            recipients=self._clean(getattr(email, "sent_to", None) or []),
            date=getattr(email, "parsed_date", None),
            subject=subject or "[ngen] mensaje entrante no legible",
            body=self._clean(
                "[ngen] No se pudo procesar este mensaje entrante; se conserva "
                "este registro para no perder la traza.\n\n%s" % error
            ),
            status=EmailMessage.Status.SENT,
            last_error=self._clean(str(error))[:2000],
        )

    def map_emails(self, emails: list) -> List[EmailMessage]:
        """
        Map a list of imbox ``(uid, message)`` pairs to EmailMessage instances,
        preserving order (one output per input). A message that cannot be parsed
        becomes a placeholder error record (see :meth:`build_error_message`)
        instead of aborting the whole batch.
        """
        mapped = []
        for uid, email in emails:
            try:
                mapped.append(self.map_email(email))
            except Exception as exc:  # noqa: BLE001 - one bad mail must not stop ingestion
                logger.exception("map_emails: unparseable message uid=%s", uid)
                mapped.append(self.build_error_message(email, exc))
        return mapped

    def get_root_message_id(self, message: Messages):
        """
        Get first message ID from References field
        """
        reference_field = self.get_references_field(message)
        return reference_field[0] if reference_field else None

    def get_parent_message_id(self, message: Messages):
        """
        Get parent message ID from In-Reply-To field
        """
        return self.get_custom_email_field(message, "In-Reply-To") or None

    def get_message_id(self, message: Messages):
        """
        Return the Message-ID of the message.

        Some malformed messages carry no Message-ID header (imbox then omits the
        attribute, which used to raise ``AttributeError`` and stall ingestion).
        In that case derive a deterministic id from the raw content, so the
        record is still unique and re-ingestion/backfill can de-duplicate it.
        """
        message_id = getattr(message, "message_id", None) if message else None
        if message_id:
            return self._bound_id(message_id)
        # Hash the raw payload faithfully (no lossy decode): two id-less messages
        # that differ only by an undecodable byte must not collide in dedup.
        raw = getattr(message, "raw_email", b"") if message else b""
        raw_bytes = raw.encode("utf-8", "surrogatepass") if isinstance(raw, str) else (raw or b"")
        digest = hashlib.sha256(raw_bytes).hexdigest()
        return "<%s@no-message-id.ngen>" % digest

    def get_references_field(self, message: Messages):
        """
        Get references field from email
        """
        return self.get_custom_email_field(message, "References").split()

    def get_custom_email_field(self, message: Messages, field: str):
        """
        Get custom field from email
        """
        raw = getattr(message, "raw_email", "") or ""
        return self.map_raw_email(raw).get(field, "")

    def map_raw_email(self, raw_email: str) -> Message:
        """
        Map raw email to Message model from python email library
        """
        return email.message_from_string(raw_email)
