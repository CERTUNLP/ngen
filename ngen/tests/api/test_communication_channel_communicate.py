from unittest.mock import patch
from django.utils import timezone
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from ngen.models import (
    EmailMessage,
    Event,
    CommunicationChannel,
    Priority,
    Tlp,
    Taxonomy,
    Feed,
    User,
    Contact,
)
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin


def use_test_email_env():
    """
    Change constance config to use test email environment
    """
    return patch.dict(
        settings.CONSTANCE_CONFIG,
        {
            "EMAIL_HOST": ("ngen-mail", ""),
            "EMAIL_SENDER": ("test@ngen.com", ""),
            "EMAIL_USERNAME": ("username", ""),
            "EMAIL_PASSWORD": ("password", ""),
            "EMAIL_PORT": ("1025", ""),
            "EMAIL_USE_TLS": (False, ""),
        },
    )


class TestCommunicationChannelCommunicate(APITestCaseWithLogin):
    """
    This will handle Communication Channel Communicate endpoint tests
    """

    fixtures = [
        "priority.json",
        "user.json",
        "taxonomy.json",
        "feed.json",
        "tlp.json",
        "contact.json",
        "network.json",
        "network_entity.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        basename = "communicationchannel"
        cls.url_detail = lambda pk: reverse(f"{basename}-detail", kwargs={"pk": pk})
        cls.url_communicate = lambda pk: cls.url_detail(pk) + "communicate/"
        cls.event = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=Taxonomy.objects.get(slug="botnet"),
            feed=Feed.objects.get(slug="csirtamericas"),
            tlp=Tlp.objects.get(slug="green"),
            reporter=User.objects.get(username="ngen"),
            notes="Some notes",
            priority=Priority.objects.get(slug="high"),
        )
        cls.communication_channel = CommunicationChannel.create_channel_with_affected(
            channelable=cls.event,
            additional_contacts=["another_contact@example.com"],
        )
        cls.contact = Contact.objects.get(pk=1)  # Contact of the network

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_communicate(self):
        """
        This will test successful POST to communicate endpoint
        """
        initial_count = EmailMessage.objects.count()
        expected_senders = [{"name": "username", "email": "test@ngen.com"}]
        expected_recipients = [
            {"name": self.contact.name, "email": self.contact.username},
            {"name": "another_contact", "email": "another_contact@example.com"},
        ]
        params = {"subject": "Test Subject", "body": "Test Body"}

        response = self.client.post(
            self.url_communicate(self.communication_channel.id), data=params
        )

        self.communication_channel.refresh_from_db()
        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)
        self.assertEqual(created_email_message.senders, expected_senders)
        self.assertEqual(created_email_message.recipients, expected_recipients)
        self.assertEqual(created_email_message.subject, params["subject"])
        self.assertEqual(created_email_message.body, params["body"])
        self.assertEqual(created_email_message.sent, True)
        self.assertIsNotNone(created_email_message.date)
        self.assertEqual(self.communication_channel.get_messages().count(), 1)
        self.assertEqual(
            self.communication_channel.get_last_message(), created_email_message
        )
        self.assertEqual(
            self.communication_channel.message_id, created_email_message.message_id
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_communicate_in_thread(self):
        """
        This will test successful POST to communicate endpoint
        when channel already has messages
        """
        root_message_id = "<172654248025.81.10116784141945641235@cert.unlp.edu.ar>"
        EmailMessage.objects.create(
            root_message_id=root_message_id,
            parent_message_id=None,
            message_id=root_message_id,
            references=[],
            subject="Test Subject",
            senders=[{"name": "CERT User", "email": "test@cert.unlp.edu.ar"}],
            recipients=[{"name": "Victim Name", "email": "victim@organization.com"}],
            date=timezone.now(),
            body="Test body",
            sent=True,
            send_attempt_failed=False,
        )
        EmailMessage.objects.create(
            root_message_id=root_message_id,
            parent_message_id=root_message_id,
            message_id="<172654293755.81.289851525536098366@cert.unlp.edu.ar>",
            references=[root_message_id],
            subject="Re: Test Subject",
            senders=[{"name": "Victim Name", "email": "victim@organization.com"}],
            recipients=[{"name": "CERT User", "email": "test@cert.unlp.edu.ar"}],
            date=timezone.now(),
            body="Test body",
            sent=True,
            send_attempt_failed=False,
        )

        self.communication_channel.message_id = root_message_id
        self.communication_channel.save()

        initial_count = EmailMessage.objects.count()
        expected_senders = [{"name": "username", "email": "test@ngen.com"}]
        expected_recipients = [
            {"name": self.contact.name, "email": self.contact.username},
            {"name": "another_contact", "email": "another_contact@example.com"},
        ]
        params = {"body": "Test Body"}

        response = self.client.post(
            self.url_communicate(self.communication_channel.id), data=params
        )

        self.communication_channel.refresh_from_db()
        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)
        self.assertEqual(created_email_message.senders, expected_senders)
        self.assertEqual(created_email_message.recipients, expected_recipients)
        self.assertEqual(created_email_message.subject, "Re: Test Subject")
        self.assertEqual(created_email_message.body, params["body"])
        self.assertEqual(created_email_message.sent, True)
        self.assertIsNotNone(created_email_message.date)
        self.assertEqual(self.communication_channel.get_messages().count(), 3)
        self.assertEqual(
            self.communication_channel.get_last_message(), created_email_message
        )
        self.assertNotEqual(
            self.communication_channel.message_id, created_email_message.message_id
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_communicate_without_body(self):
        """
        This will test unsuccessful POST to communicate endpoint
        without body
        """
        initial_count = EmailMessage.objects.count()

        params = {"subject": "Test Subject"}

        response = self.client.post(
            self.url_communicate(self.communication_channel.id), data=params
        )

        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(EmailMessage.objects.count(), initial_count)
        self.assertIn(
            "Body is required",
            response_messages["error"],
        )
