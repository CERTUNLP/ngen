"""
Django Unit Tests for EmailMessage model
"""

from django.utils import timezone
from django.test import TestCase

from ngen.models import EmailMessage


class EmailMessageTest(TestCase):
    """
    This will handle EmailMessage model tests
    """

    @classmethod
    def setUpTestData(cls):
        """
        EmailMessage model test setup
        """
        cls.root_email_message = EmailMessage.objects.create(
            root_message_id="4e58452c-37af-4f8d-a4fd-36b4c3cb11fc",
            message_id="4e58452c-37af-4f8d-a4fd-36b4c3cb11fc",
            sender="sender",
            recipient="recipient",
            date=timezone.now(),
            body="some body",
        )
        cls.email_message_2 = EmailMessage.objects.create(
            root_message_id="4e58452c-37af-4f8d-a4fd-36b4c3cb11fc",
            parent_message_id="4e58452c-37af-4f8d-a4fd-36b4c3cb11fc",
            message_id="0d8fb56f-9151-4a86-b6b3-86e9a0d4c654",
            sender="sender",
            recipient="recipient",
            date=timezone.now() + timezone.timedelta(hours=1),
            body="some body",
        )
        cls.email_message_3 = EmailMessage.objects.create(
            root_message_id="4e58452c-37af-4f8d-a4fd-36b4c3cb11fc",
            parent_message_id="0d8fb56f-9151-4a86-b6b3-86e9a0d4c654",
            message_id="e509e60b-0a6e-448c-843f-dcf3feaa85f6",
            sender="sender",
            recipient="recipient",
            date=timezone.now() + timezone.timedelta(hours=2),
            body="some body",
        )
        cls.email_message_4 = EmailMessage.objects.create(
            root_message_id="4e58452c-37af-4f8d-a4fd-36b4c3cb11fc",
            parent_message_id="e509e60b-0a6e-448c-843f-dcf3feaa85f6",
            message_id="c7693444-b42e-4032-8e82-5d11af7553b2",
            sender="sender",
            recipient="recipient",
            date=timezone.now() + timezone.timedelta(hours=3),
            body="some body",
        )

    def test_email_message_creation(self):
        """
        This will test EmailMessage creation
        """
        self.assertTrue(isinstance(self.root_email_message, EmailMessage))
        self.assertTrue(isinstance(self.email_message_2, EmailMessage))
        self.assertTrue(isinstance(self.email_message_3, EmailMessage))
        self.assertTrue(isinstance(self.email_message_4, EmailMessage))

    def test_get_message_thread_by(self):
        """
        This will test EmailMessage get_message_thread_by method
        """
        expected_messages = [
            self.root_email_message,
            self.email_message_2,
            self.email_message_3,
            self.email_message_4,
        ]
        email_messages = EmailMessage.get_message_thread_by(
            "4e58452c-37af-4f8d-a4fd-36b4c3cb11fc"
        )

        self.assertQuerysetEqual(email_messages, expected_messages)

        non_existent = EmailMessage.get_message_thread_by("non-existent")
        self.assertEqual(non_existent.count(), 0)
