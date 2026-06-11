import json
from unittest.mock import patch, MagicMock
from django.test import override_settings
from django.core import mail
from constance.test import override_config

from ngen.models import EmailMessage
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin
from ngen.tests.test_helpers import use_test_email_env

CELERY_EAGER = override_settings(CELERY_TASK_ALWAYS_EAGER=True)


def _make_email(**kwargs):
    defaults = {
        "root_message_id": "<t@ngen.com>",
        "message_id": "<t@ngen.com>",
        "senders": [{"name": "test", "email": "test@ngen.com"}],
        "recipients": [{"name": "to", "email": "to@test.com"}],
        "subject": "Test",
        "body": "Body",
    }
    defaults.update(kwargs)
    if "root_message_id" in kwargs and "message_id" not in kwargs:
        defaults["message_id"] = kwargs["root_message_id"]
    return EmailMessage.objects.create(**defaults)


class TestSendQueuedEndpoint(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_list = cls.url_list = "/api/emailmessage/"

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.views.email_message.async_send_email.delay")
    def test_send_queued_dispatches_and_returns_200(self, mock_delay):
        msg = _make_email(dispatched=False, sent=False)
        response = self.client.post(f"{self.url_list}{msg.id}/send/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "dispatched")
        mock_delay.assert_called_once_with(msg.id)

    @use_test_email_env()
    @CELERY_EAGER
    def test_send_queued_rejects_already_sent(self):
        msg = _make_email(dispatched=False, sent=True)
        response = self.client.post(f"{self.url_list}{msg.id}/send/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("already sent", response.data["error"])

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.views.email_message.async_send_email.delay")
    def test_send_queued_allows_limbo_dispatched(self, mock_delay):
        msg = _make_email(dispatched=True, sent=False)
        response = self.client.post(f"{self.url_list}{msg.id}/send/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "dispatched")
        mock_delay.assert_called_once_with(msg.id)


class TestSendAllPendingEndpoint(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_list = "/api/emailmessage/"

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.views.email_message.async_send_email.delay")
    def test_send_all_pending_dispatches(self, mock_delay):
        _make_email(dispatched=False, sent=False, send_attempt_failed=False,
                    root_message_id="<a@t.com>", message_id="<a@t.com>")
        _make_email(dispatched=False, sent=False, send_attempt_failed=False,
                    root_message_id="<b@t.com>", message_id="<b@t.com>")
        response = self.client.post(f"{self.url_list}send_all_pending/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(mock_delay.call_count, 2)

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.views.email_message.async_send_email.delay")
    def test_send_all_pending_empty(self, mock_delay):
        response = self.client.post(f"{self.url_list}send_all_pending/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        mock_delay.assert_not_called()

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.views.email_message.async_send_email.delay")
    def test_send_all_pending_skips_failed_and_sent(self, mock_delay):
        _make_email(dispatched=False, sent=False, send_attempt_failed=False,
                    root_message_id="<p@t.com>", message_id="<p@t.com>")
        _make_email(dispatched=False, sent=False, send_attempt_failed=True,
                    root_message_id="<f@t.com>", message_id="<f@t.com>")
        _make_email(dispatched=False, sent=True, send_attempt_failed=False,
                    root_message_id="<s@t.com>", message_id="<s@t.com>")
        response = self.client.post(f"{self.url_list}send_all_pending/")
        self.assertEqual(response.data["count"], 1)
        mock_delay.assert_called_once()

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.views.email_message.async_send_email.delay")
    def test_send_all_pending_includes_limbo_emails(self, mock_delay):
        _make_email(dispatched=False, sent=False, send_attempt_failed=False,
                    root_message_id="<p@t.com>", message_id="<p@t.com>")
        _make_email(dispatched=True, sent=False, send_attempt_failed=False,
                    root_message_id="<l@t.com>", message_id="<l@t.com>")
        response = self.client.post(f"{self.url_list}send_all_pending/")
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(mock_delay.call_count, 2)


class TestResendEndpoint(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_list = "/api/emailmessage/"

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.views.email_message.async_send_email.delay")
    def test_resend_clones_and_dispatches_regardless_of_auto_send(self, mock_delay):
        original = _make_email(
            sent=True, dispatched=True, send_attempt_failed=False,
            subject="Original", body_html="<p>html</p>",
            template="case_report", attachments=[],
            bcc_recipients=[{"name": "bcc", "email": "bcc@t.com"}],
        )
        with override_config(EMAIL_AUTO_SEND=False):
            response = self.client.post(f"{self.url_list}{original.id}/resend/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "cloned")
        self.assertEqual(response.data["original_id"], original.id)
        self.assertNotEqual(response.data["id"], original.id)
        mock_delay.assert_called_once()

        clone = EmailMessage.objects.get(id=response.data["id"])
        self.assertEqual(clone.subject, "Original")
        self.assertEqual(clone.body_html, "<p>html</p>")
        self.assertEqual(clone.template, "case_report")
        self.assertEqual(clone.bcc_recipients, [{"name": "bcc", "email": "bcc@t.com"}])
        self.assertTrue(clone.dispatched)


class TestDiscardEndpoint(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_list = "/api/emailmessage/"

    @use_test_email_env()
    @CELERY_EAGER
    def test_discard_marks_as_failed_with_default_reason(self):
        msg = _make_email(dispatched=False, sent=False, send_attempt_failed=False)
        response = self.client.post(f"{self.url_list}{msg.id}/discard/", {}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "discarded")
        msg.refresh_from_db()
        self.assertTrue(msg.send_attempt_failed)
        self.assertEqual(msg.last_error, "cancelado por usuario")

    @use_test_email_env()
    @CELERY_EAGER
    def test_discard_marks_as_failed_with_custom_reason(self):
        msg = _make_email(dispatched=False, sent=False, send_attempt_failed=False)
        response = self.client.post(f"{self.url_list}{msg.id}/discard/", {"reason": "spam"}, format="json")
        self.assertEqual(response.status_code, 200)
        msg.refresh_from_db()
        self.assertEqual(msg.last_error, "spam")

    @use_test_email_env()
    @CELERY_EAGER
    def test_discard_rejects_already_sent(self):
        msg = _make_email(dispatched=True, sent=True, send_attempt_failed=False)
        response = self.client.post(f"{self.url_list}{msg.id}/discard/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("already sent", response.data["error"])

    @use_test_email_env()
    @CELERY_EAGER
    def test_discard_allows_limbo_dispatched(self):
        msg = _make_email(dispatched=True, sent=False, send_attempt_failed=False)
        response = self.client.post(f"{self.url_list}{msg.id}/discard/", {}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "discarded")
        msg.refresh_from_db()
        self.assertTrue(msg.send_attempt_failed)


class TestRetryEndpoint(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_list = "/api/emailmessage/"

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.views.email_message.async_send_email.delay")
    def test_retry_clones_failed_and_dispatches(self, mock_delay):
        original = _make_email(
            dispatched=True, sent=False, send_attempt_failed=True, retried=False,
            subject="Failed email", last_error="SMTP timeout",
            body_html="<p>test</p>", template="case_closed_report",
            bcc_recipients=[{"name": "bcc", "email": "b@t.com"}],
        )
        response = self.client.post(f"{self.url_list}{original.id}/retry/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "retried")
        self.assertEqual(response.data["original_id"], original.id)

        clone = EmailMessage.objects.get(id=response.data["id"])
        self.assertEqual(clone.subject, "Failed email")
        self.assertEqual(clone.body_html, "<p>test</p>")
        self.assertTrue(clone.dispatched)
        self.assertFalse(clone.send_attempt_failed)
        original.refresh_from_db()
        self.assertTrue(original.retried)
        mock_delay.assert_called_once()

    @use_test_email_env()
    @CELERY_EAGER
    def test_retry_rejects_non_failed(self):
        msg = _make_email(dispatched=False, sent=True, send_attempt_failed=False)
        response = self.client.post(f"{self.url_list}{msg.id}/retry/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("only failed", response.data["error"].lower() if isinstance(response.data.get("error"), str) else "")

    @use_test_email_env()
    @CELERY_EAGER
    def test_retry_rejects_already_retried(self):
        msg = _make_email(sent=False, send_attempt_failed=True, retried=True)
        response = self.client.post(f"{self.url_list}{msg.id}/retry/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("already retried", response.data["error"])


class TestStatsEndpoint(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_list = "/api/emailmessage/"

    @use_test_email_env()
    def test_stats_all_empty(self):
        response = self.client.get(f"{self.url_list}stats/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["pending"], 0)
        self.assertEqual(response.data["failed"], 0)
        self.assertEqual(response.data["total"], 0)
        self.assertEqual(response.data["sent_total"], 0)
        self.assertIn("auto_send", response.data)

    @use_test_email_env()
    def test_stats_with_mixed_states(self):
        _make_email(sent=False, dispatched=False, send_attempt_failed=False,
                    root_message_id="<p@t.com>", message_id="<p@t.com>")
        _make_email(sent=False, dispatched=False, send_attempt_failed=False,
                    root_message_id="<p2@t.com>", message_id="<p2@t.com>")
        _make_email(sent=False, dispatched=False, send_attempt_failed=True,
                    root_message_id="<f@t.com>", message_id="<f@t.com>")
        _make_email(sent=True, dispatched=True, send_attempt_failed=False,
                    root_message_id="<s@t.com>", message_id="<s@t.com>")
        response = self.client.get(f"{self.url_list}stats/")
        self.assertEqual(response.data["pending"], 2)
        self.assertEqual(response.data["failed"], 1)
        self.assertEqual(response.data["total"], 4)
        self.assertEqual(response.data["sent_total"], 1)


class TestAsyncSendEmailEdgeCases(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.tasks.EmailBackend")
    def test_async_send_sets_size_and_date(self, mock_backend):
        from ngen.tasks import async_send_email
        mock_backend.return_value = mail.get_connection("django.core.mail.backends.locmem.EmailBackend")

        msg = _make_email(body="Hello world")
        result = async_send_email(msg.id)
        self.assertEqual(result["status"], "success")
        msg.refresh_from_db()
        self.assertIsNotNone(msg.size)
        self.assertIsNotNone(msg.date)
        self.assertGreater(msg.size, 0)

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.tasks.EmailBackend")
    def test_async_send_with_threading_headers(self, mock_backend):
        from ngen.tasks import async_send_email
        mock_backend.return_value = mail.get_connection("django.core.mail.backends.locmem.EmailBackend")

        msg = _make_email(
            parent_message_id="<parent@t.com>",
            references=["<ref1@t.com>", "<ref2@t.com>"],
            root_message_id="<root@t.com>",
            message_id="<child@t.com>",
        )
        result = async_send_email(msg.id)
        self.assertEqual(result["status"], "success")

    @use_test_email_env()
    @CELERY_EAGER
    def test_async_send_max_retries_returns_error(self):
        from ngen.tasks import async_send_email
        result = async_send_email(0)
        self.assertEqual(result["status"], "error")


class TestRetrieveEmailsFullFlow(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.tasks.EmailClient")
    def test_retrieve_emails_successful_empty(self, mock_client_class):
        from ngen.tasks import retrieve_emails
        mock_client = MagicMock()
        mock_client.fetch_unread_emails.return_value = []
        mock_client_class.return_value = mock_client

        result = retrieve_emails()
        self.assertEqual(result["status"], "success")
        self.assertIn("0 new email", result["message"])
        mock_client.logout.assert_called_once()

    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.tasks.EmailClient")
    def test_retrieve_emails_with_unread_stores_and_marks_read(self, mock_client_class):
        from ngen.tasks import retrieve_emails
        mock_client = MagicMock()
        mock_client.fetch_unread_emails.return_value = [("uid1", MagicMock())]
        mock_client.map_emails.return_value = [EmailMessage(
            root_message_id="<inc@t.com>",
            message_id="<inc@t.com>",
            senders=[{"name": "from", "email": "from@t.com"}],
            recipients=[{"name": "to", "email": "to@t.com"}],
            subject="Incoming",
            body="Body",
            sent=True,
        )]
        mock_client_class.return_value = mock_client

        result = retrieve_emails()
        self.assertEqual(result["status"], "success")
        self.assertIn("1 new email", result["message"])
        mock_client.mark_emails_as_read.assert_called_once()
        mock_client.logout.assert_called_once()


class TestEmailHandlerValidation(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    @use_test_email_env()
    def test_no_recipients_raises(self):
        from ngen.mailer.email_handler import EmailHandler
        handler = EmailHandler()
        with self.assertRaises(ValueError):
            handler.send_email(recipients=[], subject="Test", body="Body")

    @use_test_email_env()
    def test_no_subject_raises(self):
        from ngen.mailer.email_handler import EmailHandler
        handler = EmailHandler()
        with self.assertRaises(ValueError):
            handler.send_email(recipients=["to@test.com"], body="Body")

    @use_test_email_env()
    def test_neither_body_nor_template_raises(self):
        from ngen.mailer.email_handler import EmailHandler
        handler = EmailHandler()
        with self.assertRaises(ValueError):
            handler.send_email(recipients=["to@test.com"], subject="Test")

    @use_test_email_env()
    def test_invalid_template_raises(self):
        from ngen.mailer.email_handler import EmailHandler
        handler = EmailHandler()
        with self.assertRaises(ValueError):
            handler.send_email(
                recipients=["to@test.com"], subject="Test",
                template="invalid_template_name",
            )

    @use_test_email_env()
    def test_invalid_recipient_email_raises(self):
        from ngen.mailer.email_handler import EmailHandler
        handler = EmailHandler()
        with self.assertRaises(ValueError):
            handler.send_email(
                recipients=["not-an-email"], subject="Test", body="Body"
            )


class TestCommunicationSendMailEdgeCases(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=False)
    def test_bcc_only_recipients(self):
        from ngen.models.announcement import Communication
        count_before = EmailMessage.objects.count()
        Communication.send_mail(
            "BCC test",
            {"text": "body", "html": "<p>body</p>"},
            {"to": [], "cc": [], "bcc": ["bcc@test.com"]},
        )
        self.assertEqual(EmailMessage.objects.count(), count_before + 1)
        msg = EmailMessage.objects.last()
        self.assertEqual(msg.subject, "BCC test")
        self.assertEqual(len(msg.bcc_recipients), 1)
        self.assertEqual(msg.bcc_recipients[0]["email"], "bcc@test.com")

    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=False)
    def test_cc_merged_into_recipients(self):
        from ngen.models.announcement import Communication
        Communication.send_mail(
            "CC test",
            {"text": "body", "html": "<p>body</p>"},
            {"to": ["to@test.com"], "cc": ["cc@test.com"], "bcc": []},
        )
        msg = EmailMessage.objects.last()
        recipient_emails = [r["email"] for r in msg.recipients]
        self.assertIn("to@test.com", recipient_emails)
        self.assertIn("cc@test.com", recipient_emails)


class TestSendContactChecksRecords(APITestCaseWithLogin):
    fixtures = ["tests/priority.json", "tests/user.json", "tests/taxonomy.json", "tests/feed.json", "tests/tlp.json",
                "tests/contact.json", "tests/network_entity.json", "tests/network.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    @CELERY_EAGER
    @override_config(FRONTEND_PUBLIC_URL="http://test.com")
    @override_config(EMAIL_AUTO_SEND=True)
    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    def test_send_contact_checks_creates_contactcheck_records(self, mock_backend):
        from ngen.tasks import send_contact_checks
        from ngen.models.constituency import ContactCheck
        from ngen.models import Contact, Priority

        mock_backend.return_value = mail.get_connection("django.core.mail.backends.locmem.EmailBackend")

        priority = Priority.objects.get(name="High")
        contact = Contact.objects.create(
            username="ccflow@test.com", type="email", name="Check", priority=priority,
        )

        initial_count = ContactCheck.objects.count()
        send_contact_checks(contact_ids=[contact.id])
        self.assertEqual(ContactCheck.objects.count(), initial_count + 1)
        self.assertTrue(ContactCheck.objects.filter(contact=contact).exists())
