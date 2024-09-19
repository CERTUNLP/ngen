"""
Django Unit Tests for EmailMessage model
"""

from django.test import TestCase
from django.utils import timezone

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
            root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            parent_message_id=None,
            message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            references=[],
            subject="Test Subject",
            senders=[{"name": "CERT User", "email": "test@cert.unlp.edu.ar"}],
            recipients=[{"name": "Victim Name", "email": "victim@organization.com"}],
            date=timezone.now(),
            body="some body",
            sent=True,
            send_attempt_failed=False,
        )
        cls.email_message_2 = EmailMessage.objects.create(
            root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            parent_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            message_id="<172654293755.81.289851525536098366@cert.unlp.edu.ar>",
            references=["<172654248025.81.10116784141945641235@cert.unlp.edu.ar>"],
            subject="Re: Test Subject",
            senders=[{"name": "Victim Name", "email": "victim@organization.com"}],
            recipients=[{"name": "CERT User", "email": "test@cert.unlp.edu.ar"}],
            date=timezone.now(),
            body="some body",
            sent=True,
            send_attempt_failed=False,
        )
        cls.email_message_3 = EmailMessage.objects.create(
            root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            parent_message_id="<172654293755.81.289851525536098366@cert.unlp.edu.ar>",
            message_id="<172654319092.81.12026843256902635978@cert.unlp.edu.ar>",
            references=[
                "<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
                "<172654293755.81.289851525536098366@cert.unlp.edu.ar>",
            ],
            subject="Re: Test Subject",
            senders=[{"name": "Victim Name", "email": "victim@organization.com"}],
            recipients=[{"name": "CERT User", "email": "test@cert.unlp.edu.ar"}],
            date=timezone.now(),
            body="some body",
            sent=True,
            send_attempt_failed=False,
        )
        cls.email_message_4 = EmailMessage.objects.create(
            root_message_id="<172654337907.81.3069486993773407245@cert.unlp.edu.ar>",
            parent_message_id=None,
            message_id="<172654337907.81.3069486993773407245@cert.unlp.edu.ar>",
            references=[],
            subject="Test Another Subject",
            senders=[{"name": "CERT User", "email": "test@cert.unlp.edu.ar"}],
            recipients=[
                {
                    "name": "Another Victim Name",
                    "email": "another_victim@university.com",
                }
            ],
            date=timezone.now(),
            body="some body",
            sent=True,
            send_attempt_failed=False,
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
        ]
        email_messages = EmailMessage.get_message_thread_by(
            "<172654248025.81.10116784141945641235@cert.unlp.edu.ar>"
        )

        self.assertQuerysetEqual(email_messages, expected_messages)

        non_existent = EmailMessage.get_message_thread_by("non-existent")
        self.assertEqual(non_existent.count(), 0)
