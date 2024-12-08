from imbox import Imbox
from ngen.mailer.email_protocol_strategy.email_protocol_strategy import (
    EmailProtocolStrategy,
)


class IMAPStrategy(EmailProtocolStrategy):
    """
    IMAP email protocol strategy, using Imbox library
    """

    def __init__(self, host, username, password, port=993):
        super().__init__(host, username, password, port)
        self.client = None
        self.login()

    def login(self):
        self.client = Imbox(
            self.host, username=self.username, password=self.password, port=self.port
        )

    def logout(self):
        if self.client:
            self.client.logout()
            self.client = None

    def fetch_emails(self, folder: str):
        return self.client.messages(folder=folder)

    def fetch_all_emails(self):
        return self.client.messages()

    def fetch_unread_emails(self):
        return self.client.messages(unread=True)

    def mark_emails_as_read(self, emails):
        for uid, _ in emails:
            self.client.mark_seen(uid)
