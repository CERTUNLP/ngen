from os import makedirs, path
import email
from django.conf import settings
from email.message import Message
from typing import List
from imbox.messages import Messages
from ngen.mailer.email_protocol_strategy.email_protocol_strategy import (
    EmailProtocolStrategy,
)
from ngen.mailer.email_protocol_strategy.imap_strategy import IMAPStrategy
from ngen.models.email_message import EmailMessage


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
        protocol: EmailProtocolStrategy = IMAPStrategy,
    ):

        self.protocol = protocol(
            host=host, username=username, password=password, port=port
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
        Map email message and its attachments to EmailMessage model
        """

        email_message = EmailMessage(
            root_message_id=self.get_root_message_id(email)
            or self.get_message_id(email),
            parent_message_id=self.get_parent_message_id(email),
            references=self.get_references_field(email),
            message_id=self.get_message_id(email),
            senders=email.sent_from,
            recipients=email.sent_to,
            date=email.parsed_date,
            subject=email.subject.strip().replace("\r", "").replace("\n", ""),
            body=email.body["plain"][0],
            sent=True,
        )

        attachments = []

        for attachment in email.attachments:
            filename = attachment.get("filename")
            content = attachment.get("content")

            if not filename or not content:
                continue

            attachment_path = email_message.attachment_path(filename)
            download_path = path.join(settings.MEDIA_ROOT, attachment_path)
            makedirs(path.dirname(download_path), exist_ok=True)

            try:
                with open(download_path, "wb") as file:
                    file.write(content.read())

                attachments.append(
                    {
                        "name": filename,
                        "file": attachment_path,
                    }
                )
            except IOError as e:
                print(f"Failed to save attachment {filename}: {e}")

        email_message.attachments = attachments

        return email_message

    def map_emails(self, emails: list) -> List[EmailMessage]:
        """
        Map a list of email messages to a list of EmailMessage model, using EmailClient.map_email helper method
        """
        return [self.map_email(email) for uid, email in emails]

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
        Get message ID from Message-ID field
        """
        return message.message_id if message else None

    def get_references_field(self, message: Messages):
        """
        Get references field from email
        """
        return self.get_custom_email_field(message, "References").split()

    def get_custom_email_field(self, message: Messages, field: str):
        """
        Get custom field from email
        """
        return self.map_raw_email(message.raw_email).get(field, "")

    def map_raw_email(self, raw_email: str) -> Message:
        """
        Map raw email to Message model from python email library
        """
        return email.message_from_string(raw_email)
