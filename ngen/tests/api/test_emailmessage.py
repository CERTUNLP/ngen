import json
from unittest.mock import patch
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from constance import config

from ngen.models import EmailMessage
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin
from ngen.tests.test_helpers import use_incorrect_email_env, use_test_email_env


class TestEmailMessage(APITestCaseWithLogin):
    """
    This will handle Email Message API tests
    """

    fixtures = [
        "tests/priority.json",
        "tests/user.json",
        "tests/taxonomy.json",
        "tests/feed.json",
        "tests/tlp.json",
    ]

    @classmethod
    @use_test_email_env()
    def setUpTestData(cls):
        super().setUpTestData()
        basename = "emailmessage"
        cls.url_list = reverse(f"{basename}-list")
        cls.url_detail = lambda pk: reverse(f"{basename}-detail", kwargs={"pk": pk})
        cls.url_send_email = cls.url_list + "send_email/"
        cls.app_email_sender = config.EMAIL_SENDER
        cls.app_email_username = config.EMAIL_USERNAME

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_email_message_get_list(self):
        """
        This will test successful Email Message GET list
        """
        email_messages = [
            EmailMessage.objects.create(
                root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
                parent_message_id=None,
                message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
                references=[],
                subject="Test Subject",
                senders=[
                    {"name": self.app_email_username, "email": self.app_email_sender}
                ],
                recipients=[
                    {"name": "Victim Name", "email": "victim@organization.com"}
                ],
                date=timezone.now(),
                body="Test body",
                sent=True,
                send_attempt_failed=False,
            ),
            EmailMessage.objects.create(
                root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
                parent_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
                message_id="<172654293755.81.289851525536098366@cert.unlp.edu.ar>",
                references=["<172654248025.81.10116784141945641235@cert.unlp.edu.ar>"],
                subject="Re: Test Subject",
                senders=[{"name": "Victim Name", "email": "victim@organization.com"}],
                recipients=[
                    {"name": self.app_email_username, "email": self.app_email_sender}
                ],
                date=timezone.now(),
                body="Test body",
                sent=True,
                send_attempt_failed=False,
            ),
        ]

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(email_messages))
        self.assertEqual(
            response.data["results"][0]["message_id"],
            email_messages[0].message_id,
        )
        self.assertEqual(
            response.data["results"][1]["message_id"],
            email_messages[1].message_id,
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_email_message_get_detail(self):
        """
        This will test successful Email Message GET detail
        """

        email_message = EmailMessage.objects.create(
            root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            parent_message_id=None,
            message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            references=[],
            subject="Test Subject",
            senders=[{"name": self.app_email_username, "email": self.app_email_sender}],
            recipients=[{"name": "Victim Name", "email": "victim@organization.com"}],
            date=timezone.now(),
            body="Test body",
            sent=True,
            send_attempt_failed=False,
        )

        response = self.client.get(self.url_detail(email_message.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message_id"], email_message.message_id)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_email_message_patch(self):
        """
        This will test successful Communication Channel PUT
        """

        email_message = EmailMessage.objects.create(
            root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            parent_message_id=None,
            message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            references=[],
            subject="Test Subject",
            senders=[{"name": self.app_email_username, "email": self.app_email_sender}],
            recipients=[{"name": "Victim Name", "email": "victim@organization.com"}],
            date=timezone.now(),
            body="Test body",
            sent=True,
            send_attempt_failed=False,
        )

        json_data = {"body": "New body"}

        response = self.client.patch(self.url_detail(email_message.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        email_message.refresh_from_db()
        self.assertEqual(email_message.body, "New body")

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_without_subject(self):
        """
        This will test unsuccessful send email without subject
        """

        json_data = {
            "recipients": [{"name": "Victim Name", "email": "victim@organization.com"}],
            "body": "Test body",
        }

        response = self.client.post(self.url_send_email, data=json_data)

        response_messages = self.get_messages_from_response(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Subject not provided",
            response_messages["error"],
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_without_recipients(self):
        """
        This will test unsuccessful send email without subject
        """

        json_data = {
            "recipients": [],
            "subject": "Test Subject",
            "body": "Test body",
        }

        response = self.client.post(self.url_send_email, data=json_data)

        response_messages = self.get_messages_from_response(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Recipients not provided",
            response_messages["error"],
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_invalid_recipient_key(self):
        """
        This will test unsuccessful send email with invalid recipients
        """

        json_data = {
            "recipients": [
                {"name": "Victim Name", "address": "victim@organization.com"}
            ],
            "subject": "Correo desde NGEN",
            "body": "Respondiendo al primer email",
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        response_messages = self.get_messages_from_response(response)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn(
            "There was an error sending the email.",
            response_messages["error"],
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_invalid_recipient_email(self):
        """
        This will test unsuccessful send email with invalid recipient email format
        """

        json_data = {
            "recipients": [
                {"name": "Correct format", "email": "correct@format.com"},
                {"name": "Incorrect format", "email": "incorrect@format"},
            ],
            "subject": "Test Subject",
            "body": "Test body",
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        response_messages = self.get_messages_from_response(response)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn(
            "There was an error sending the email.",
            response_messages["error"],
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_invalid_recipient_format(self):
        """
        This will test unsuccessful send email with invalid recipients format
        """

        json_data = {
            "recipients": "victim@organization.com",
            "subject": "Test Subject",
            "body": "Test body",
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        response_messages = self.get_messages_from_response(response)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn(
            "There was an error sending the email.",
            response_messages["error"],
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_non_existent_in_reply_to_email_message(self):
        """
        This will test unsuccessful send email with non-existent in_reply_to email message
        """

        json_data = {
            "recipients": [{"name": "Victim Name", "email": "victim@organization.com"}],
            "subject": "Test Subject",
            "body": "Test body",
            "in_reply_to": 9999,
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        response_messages = self.get_messages_from_response(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Invalid 'in_reply_to' parameter. Email Message with ID '9999' does not exist.",
            response_messages["error"],
        )

    @patch("ngen.tasks.async_send_email.delay")
    def test_async_send_email_task_is_called(self, mocked_send_email_task):
        """
        This will test that the async_send_email task is called with the correct arguments
        """

        json_data = {
            "recipients": [{"name": "Victim Name", "email": "victim@organization.com"}],
            "subject": "Test Subject",
            "body": "Test body",
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        mocked_send_email_task.assert_called_once_with(response.data["id"])

    @use_incorrect_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_async_send_email_task_fails(self):
        """
        This will test that the async_send_email task fails
        """

        initial_count = EmailMessage.objects.count()

        json_data = {
            "recipients": [{"name": "Victim Name", "email": "victim@organization.com"}],
            "subject": "Test Subject Fail Email",
            "body": "Test body",
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(created_email_message.subject, "Test Subject Fail Email")
        self.assertEqual(created_email_message.sent, False)
        self.assertEqual(created_email_message.send_attempt_failed, True)
        self.assertEqual(created_email_message.date, None)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email(self):
        """
        This will test successful send email
        """

        initial_count = EmailMessage.objects.count()

        json_data = {
            "recipients": [{"name": "Victim Name", "email": "victim@organization.com"}],
            "subject": "Test Subject Success Email",
            "body": "Test body",
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(created_email_message.subject, "Test Subject Success Email")
        self.assertEqual(
            created_email_message.senders,
            [{"name": self.app_email_username, "email": self.app_email_sender}],
        )
        self.assertEqual(created_email_message.recipients, json_data["recipients"])
        self.assertEqual(created_email_message.body, json_data["body"])
        self.assertEqual(created_email_message.sent, True)
        self.assertIsNotNone(created_email_message.date)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_in_reply_to(self):
        """
        This will test successful send email with in_reply_to
        """

        email_message = EmailMessage.objects.create(
            root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            parent_message_id=None,
            message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            references=[],
            subject="Test Subject",
            senders=[{"name": "Victim Name", "email": "victim@organization.com"}],
            recipients=[
                {"name": self.app_email_username, "email": self.app_email_sender}
            ],
            date=timezone.now(),
            body="Test body",
            sent=True,
            send_attempt_failed=False,
        )

        initial_count = EmailMessage.objects.count()

        json_data = {
            "subject": "Test Subject Success Email",
            "body": "Test body",
            "in_reply_to": email_message.id,
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(created_email_message.subject, f"Re: {email_message.subject}")
        self.assertEqual(
            created_email_message.senders,
            [{"name": self.app_email_username, "email": self.app_email_sender}],
        )
        self.assertEqual(created_email_message.recipients, email_message.senders)
        self.assertEqual(created_email_message.sent, True)
        self.assertIsNotNone(created_email_message.date)
        self.assertEqual(
            created_email_message.root_message_id, email_message.message_id
        )
        self.assertEqual(
            created_email_message.parent_message_id, email_message.message_id
        )
        self.assertEqual(created_email_message.references, [email_message.message_id])

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_in_thread(self):
        """
        This will test successful send email in a thread
        """

        email_messages = [
            EmailMessage.objects.create(
                root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
                parent_message_id=None,
                message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
                references=[],
                subject="Test Subject",
                senders=[
                    {"name": self.app_email_username, "email": self.app_email_sender}
                ],
                recipients=[
                    {"name": "Victim Name", "email": "victim@organization.com"}
                ],
                date=timezone.now(),
                body="Test body",
                sent=True,
                send_attempt_failed=False,
            ),
            EmailMessage.objects.create(
                root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
                parent_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
                message_id="<172654293755.81.289851525536098366@cert.unlp.edu.ar>",
                references=["<172654248025.81.10116784141945641235@cert.unlp.edu.ar>"],
                subject="Re: Test Subject",
                senders=[{"name": "Victim Name", "email": "victim@organization.com"}],
                recipients=[
                    {"name": self.app_email_username, "email": self.app_email_sender}
                ],
                date=timezone.now(),
                body="Test body",
                sent=True,
                send_attempt_failed=False,
            ),
        ]

        initial_count = EmailMessage.objects.count()

        json_data = {
            "recipients": [{"name": "Victim Name", "email": "victim@organization.com"}],
            "subject": "Test Subject Success Email",
            "body": "Test body",
            "in_reply_to": email_messages[1].id,
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(created_email_message.subject, email_messages[1].subject)
        self.assertEqual(
            created_email_message.senders,
            [{"name": self.app_email_username, "email": self.app_email_sender}],
        )
        self.assertEqual(created_email_message.recipients, email_messages[1].senders)
        self.assertEqual(created_email_message.sent, True)
        self.assertIsNotNone(created_email_message.date)
        self.assertEqual(
            created_email_message.root_message_id, email_messages[0].message_id
        )
        self.assertEqual(
            created_email_message.parent_message_id, email_messages[1].message_id
        )
        self.assertEqual(
            created_email_message.references,
            [email_messages[0].message_id, email_messages[1].message_id],
        )

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_template_and_template_params(self):
        """
        This will test successful send email
        """

        initial_count = EmailMessage.objects.count()

        json_data = {
            "recipients": [{"name": "Victim Name", "email": "victim@organization.com"}],
            "subject": "Test Subject Success Email",
            "body": "Test body",
            "template": "case_report",
            "template_params": {"param1": "value1", "param2": "value2"},
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(created_email_message.template, json_data["template"])

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_many_recipients(self):
        """
        This will test successful send email with many recipients
        """

        initial_count = EmailMessage.objects.count()

        json_data = {
            "recipients": [
                {"name": "Victim Name", "email": "victim@organization.com"},
                {"name": "Victim Name 2", "email": "victim2@organization2.com"},
            ],
            "subject": "Test Subject Success Email",
            "body": "Test body",
        }

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(created_email_message.subject, "Test Subject Success Email")
        self.assertEqual(
            created_email_message.senders,
            [{"name": self.app_email_username, "email": self.app_email_sender}],
        )
        self.assertEqual(created_email_message.recipients, json_data["recipients"])
        self.assertEqual(created_email_message.body, json_data["body"])
        self.assertEqual(created_email_message.sent, True)
        self.assertIsNotNone(created_email_message.date)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_many_recipients_as_list(self):
        """
        This will test successful send email with many recipients as list
        """

        initial_count = EmailMessage.objects.count()

        json_data = {
            "recipients": ["victim@organization.com", "victim2@organization2.com"],
            "subject": "Test Subject Success Email",
            "body": "Test body",
        }

        expected_recipients = [
            {"name": "victim", "email": "victim@organization.com"},
            {"name": "victim2", "email": "victim2@organization2.com"},
        ]

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(created_email_message.subject, "Test Subject Success Email")
        self.assertEqual(
            created_email_message.senders,
            [{"name": self.app_email_username, "email": self.app_email_sender}],
        )
        self.assertEqual(created_email_message.recipients, expected_recipients)
        self.assertEqual(created_email_message.body, json_data["body"])
        self.assertEqual(created_email_message.sent, True)
        self.assertIsNotNone(created_email_message.date)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_in_reply_to_and_different_recipient(self):
        """
        This will test successful send email with in_reply_to
        and different recipient
        """

        email_message = EmailMessage.objects.create(
            root_message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            parent_message_id=None,
            message_id="<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            references=[],
            subject="Test Subject",
            senders=[{"name": "Victim Name", "email": "victim@organization.com"}],
            recipients=[
                {"name": self.app_email_username, "email": self.app_email_sender}
            ],
            date=timezone.now(),
            body="Test body",
            sent=True,
            send_attempt_failed=False,
        )

        initial_count = EmailMessage.objects.count()

        json_data = {
            "recipients": [
                {"name": "Another Recipient", "email": "another_recipient@org.com"},
            ],
            "subject": "Test Subject Success Email",
            "body": "Test body",
            "in_reply_to": email_message.id,
        }

        expected_recipients = [
            {"name": "Victim Name", "email": "victim@organization.com"},
            {"name": "Another Recipient", "email": "another_recipient@org.com"},
        ]

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        created_email_message = EmailMessage.objects.get(id=response.data["id"])

        self.assertEqual(created_email_message.subject, f"Re: {email_message.subject}")
        self.assertEqual(
            created_email_message.senders,
            [{"name": self.app_email_username, "email": self.app_email_sender}],
        )
        self.assertEqual(created_email_message.recipients, expected_recipients)
        self.assertEqual(created_email_message.sent, True)
        self.assertIsNotNone(created_email_message.date)
        self.assertEqual(
            created_email_message.root_message_id, email_message.message_id
        )
        self.assertEqual(
            created_email_message.parent_message_id, email_message.message_id
        )
        self.assertEqual(created_email_message.references, [email_message.message_id])

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_email_with_bcc_recipients(self):
        """
        This will test successful send email with bcc recipients
        """
        bcc_recipients = [{"name": "Bcc Contact", "email": "bcc@contact.com"}]

        json_data = {
            "bcc_recipients": bcc_recipients,
            "subject": "Test Subject Success Email",
            "body": "Test body",
        }

        initial_count = EmailMessage.objects.count()

        response = self.client.post(
            self.url_send_email,
            data=json.dumps(json_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        created_email_message = EmailMessage.objects.get(id=response.data["id"])
        self.assertEqual(
            created_email_message.senders,
            [{"name": self.app_email_username, "email": self.app_email_sender}],
        )
        self.assertEqual(created_email_message.recipients, [])
        self.assertEqual(created_email_message.bcc_recipients, bcc_recipients)
        self.assertEqual(created_email_message.sent, True)
        self.assertIsNotNone(created_email_message.date)
