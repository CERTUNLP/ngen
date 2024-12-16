from abc import ABC, abstractmethod


class EmailProtocolStrategy(ABC):
    """
    Abstract class for email protocol strategy (IMAP, POP3)
    """

    def __init__(self, host, username, password, port):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

    @abstractmethod
    def login(self):
        raise NotImplementedError

    @abstractmethod
    def logout(self):
        raise NotImplementedError

    @abstractmethod
    def fetch_emails(self, folder) -> list:
        raise NotImplementedError

    @abstractmethod
    def fetch_all_emails(self) -> list:
        raise NotImplementedError

    @abstractmethod
    def fetch_unread_emails(self) -> list:
        raise NotImplementedError

    @abstractmethod
    def mark_emails_as_read(self, emails):
        raise NotImplementedError
