import email
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

    def fetch_emails(self, folder: str, flag: str) -> List[Messages]:
        """
        Fetch emails from a folder with a specific flag
        """
        return self.protocol.fetch_emails(folder, flag)

    def fetch_all_emails(self) -> List[Messages]:
        """
        Fetch all emails
        """
        return self.protocol.fetch_all_emails()

    def fetch_unread_emails(self) -> List[Messages]:
        """
        Fetch unread emails
        """
        return self.protocol.fetch_unread_emails()

    def mark_emails_as_read(self, emails: List[Messages]):
        """
        Mark emails as read
        """
        self.protocol.mark_emails_as_read(emails)

    # Helper methods

    def map_emails(self, emails: List[Messages]) -> List[EmailMessage]:
        """
        Map email messages to EmailMessage model
        """
        return [
            EmailMessage(
                root_message_id=self.get_root_message_id(message)
                or self.get_message_id(message),
                parent_message_id=self.get_parent_message_id(message),
                references=self.get_references_field(message),
                message_id=self.get_message_id(message),
                senders=message.sent_from,
                recipients=message.sent_to,
                date=message.parsed_date,
                subject=message.subject.strip().replace("\r", "").replace("\n", ""),
                body=message.body["plain"][0],
                sent=True,
            )
            for uid, message in emails
        ]

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
        Get references field from email
        """
        return self.map_raw_email(message.raw_email).get(field, "")

    def map_raw_email(self, raw_email: str) -> Message:
        """
        Map raw email to Message model from python email library
        """
        return email.message_from_string(raw_email)
