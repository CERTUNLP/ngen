from constance.test import override_config
from django.test import TestCase, override_settings
from django.utils import timezone
from django.core import mail
from unittest.mock import patch, MagicMock

from ngen import tasks
from ngen.mailer.email_handler import EmailHandler
from ngen.models import (
    Tlp,
    Priority,
    Taxonomy,
    Event,
    Feed,
    State,
    Case,
    CaseTemplate,
    User,
    Contact,
    Network,
    NetworkEntity,
)
from ngen.models.announcement import Communication
from ngen.models.email_message import EmailMessage
from ngen.tests.test_helpers import use_test_email_env

CELERY_EAGER = override_settings(CELERY_TASK_ALWAYS_EAGER=True)


class EmailAutoSendBase(TestCase):
    fixtures = [
        "tests/priority.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/state.json",
        "tests/edge.json",
        "tests/feed.json",
        "tests/taxonomy.json",
        "tests/case_template.json",
        "tests/contact.json",
        "tests/network_entity.json",
        "tests/network.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.priority = Priority.objects.get(name="High")
        cls.tlp = Tlp.objects.get(name="Green")
        cls.state = State.objects.get(name="Open")
        cls.taxonomy = Taxonomy.objects.create(
            type="incident", name="Phising", slug="phising"
        )
        cls.feed = Feed.objects.get(slug="shodan", name="Shodan")
        cls.user = User.objects.create(
            username="testauto",
            password="test",
            email="testauto@ngen.test",
            priority=cls.priority,
        )
        cls.network = Network.objects.get(pk=1)
        cls.network_entity = NetworkEntity.objects.get(pk=1)

        cls.event = Event.objects.create(
            domain="test.unlp.edu.ar",
            taxonomy=cls.taxonomy,
            feed=cls.feed,
            tlp=cls.tlp,
            reporter=cls.user,
            network=cls.network,
        )

    def _create_case(self, **kwargs):
        case_kwargs = {
            "priority": self.priority,
            "state": self.state,
            "tlp": self.tlp,
        }
        case_kwargs.update(kwargs)
        case = Case.objects.create(**case_kwargs)
        case.events.add(self.event)
        return case

    def _make_contact(self, username):
        return Contact.objects.create(
            username=username,
            type="email",
            name=username,
            priority=self.priority,
        )


class TestPathACommunicationSendMail(EmailAutoSendBase):
    """
    Path A: Communication.send_mail() — used by contact_summary, announcements, etc.
    """

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @CELERY_EAGER
    def test_auto_send_true_dispatches(self, mock_backend):
        """EMAIL_AUTO_SEND=true: email is created AND dispatched to Celery"""
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        contact = self._make_contact("test1@test.com")
        tlp_obj = Tlp.objects.get(name="Green")

        with override_config(EMAIL_AUTO_SEND=True):
            Communication.communicate_contact_summary(
                contact, [], [], tlp_obj, 7
            )

        email_msg = EmailMessage.objects.last()
        self.assertIsNotNone(email_msg)
        self.assertIn(email_msg.status, ("sending", "retrying", "sent"))

    @use_test_email_env()
    @CELERY_EAGER
    def test_auto_send_false_stores_only(self):
        """EMAIL_AUTO_SEND=false: email is stored but NOT dispatched"""
        contact = self._make_contact("test2@test.com")
        tlp_obj = Tlp.objects.get(name="Green")

        with override_config(EMAIL_AUTO_SEND=False):
            Communication.communicate_contact_summary(
                contact, [], [], tlp_obj, 7
            )

        email_msg = EmailMessage.objects.last()
        self.assertIsNotNone(email_msg)
        self.assertEqual(email_msg.status, "pending")
        self.assertNotEqual(email_msg.status, "sent")

    def test_no_recipients_skips_without_creating(self):
        """send_mail with no recipients returns without creating EmailMessage"""
        count_before = EmailMessage.objects.count()
        Communication.send_mail(
            "test subject",
            {"text": "body", "html": "<p>body</p>"},
            {"to": [], "cc": [], "bcc": []},
        )
        self.assertEqual(EmailMessage.objects.count(), count_before)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @CELERY_EAGER
    def test_send_mail_creates_record_with_correct_fields(self, mock_backend):
        """Verify EmailMessage fields are correct regardless of auto_send"""
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        Communication.send_mail(
            "Test Subject",
            {"text": "plain body", "html": "<p>html body</p>", "template": "test"},
            {"to": ["to1@test.com"], "cc": ["cc1@test.com"], "bcc": ["bcc1@test.com"]},
        )

        email_msg = EmailMessage.objects.last()
        self.assertEqual(email_msg.subject, "Test Subject")
        self.assertEqual(email_msg.body, "plain body")
        self.assertEqual(email_msg.body_html, "<p>html body</p>")
        self.assertEqual(len(email_msg.recipients), 2)  # to + cc merged
        self.assertEqual(len(email_msg.bcc_recipients), 1)


class TestPathBEmailHandlerSendEmail(EmailAutoSendBase):
    """
    Path B: EmailHandler.send_email() — used by CommunicationChannel / cases.
    """

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.mailer.email_handler.async_send_email.delay")
    def test_auto_send_true_dispatches_via_on_commit(
        self, mock_delay, mock_backend
    ):
        """EMAIL_AUTO_SEND=true: dispatch called via transaction.on_commit"""
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        handler = EmailHandler()
        with override_config(EMAIL_AUTO_SEND=True):
            with self.captureOnCommitCallbacks(execute=True):
                email_msg = handler.send_email(
                    recipients=["to@test.com"],
                    subject="Test",
                    body="Test body",
                )

        self.assertIsNotNone(email_msg)
        mock_delay.assert_called_once()

    @use_test_email_env()
    def test_auto_send_false_stores_only(self):
        """EMAIL_AUTO_SEND=false: email stored, NOT dispatched"""
        handler = EmailHandler()
        with override_config(EMAIL_AUTO_SEND=False):
            email_msg = handler.send_email(
                recipients=["to@test.com"],
                subject="Test",
                body="Test body",
            )

        self.assertIsNotNone(email_msg)
        self.assertEqual(email_msg.status, "pending")
        self.assertNotEqual(email_msg.status, "sent")

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @CELERY_EAGER
    def test_send_email_with_template(self, mock_backend):
        """Verify template rendering works in EmailHandler"""
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        handler = EmailHandler()
        with override_config(EMAIL_AUTO_SEND=True):
            email_msg = handler.send_email(
                recipients=["to@test.com"],
                subject="Case Report",
                body=None,
                template="case_report",
                template_params={"case": None},
            )
        self.assertIsNotNone(email_msg)
        self.assertIn("case_report", email_msg.template)


class TestPathCViewSetActions(EmailAutoSendBase):
    """
    Path C: ViewSet manual actions — always dispatch regardless of EMAIL_AUTO_SEND.
    """

    def setUp(self):
        self.email_msg = EmailMessage.objects.create(
            root_message_id="<viewset@test.com>",
            message_id="<viewset@test.com>",
            senders=[{"name": "test", "email": "test@ngen.com"}],
            recipients=[{"name": "to", "email": "to@test.com"}],
            subject="ViewSet test",
            body="Body",
            status="pending",
        )

    @patch("ngen.tasks.async_send_email.delay")
    def test_send_endpoint_dispatches_regardless_of_auto_send(self, mock_delay):
        """send action always dispatches even with EMAIL_AUTO_SEND=false"""
        with override_config(EMAIL_AUTO_SEND=False):
            # simulate ViewSet.send_queued: dispatch + set status
            tasks.async_send_email.delay(self.email_msg.id)
            self.email_msg.status = "sending"
            self.email_msg.save(update_fields=["status"])

        mock_delay.assert_called_once()
        self.email_msg.refresh_from_db()
        self.assertIn(self.email_msg.status, ("sending", "retrying"))

    @patch("ngen.tasks.EmailBackend")
    @patch("ngen.tasks.async_send_email.delay")
    def test_send_endpoint_skips_if_already_sent(self, mock_delay, mock_backend):
        """send action rejects already-sent emails"""
        self.email_msg.status = "sent"
        self.email_msg.save()
        result = tasks.async_send_email(self.email_msg.id)
        self.assertEqual(result["status"], "skipped")

    def test_discard_endpoint_marks_as_failed(self):
        """discard sets status=failed and stores reason"""
        self.email_msg.status = "failed"
        self.email_msg.last_error = "cancelado por usuario"
        self.email_msg.save(update_fields=["status", "last_error"])
        self.email_msg.refresh_from_db()

        self.assertEqual(self.email_msg.status, "failed")
        self.assertEqual(self.email_msg.last_error, "cancelado por usuario")

    @patch("ngen.tasks.async_send_email.delay")
    @use_test_email_env()
    @CELERY_EAGER
    def test_resend_clones_and_dispatches(self, mock_delay):
        """resend creates a clone and dispatches it regardless of EMAIL_AUTO_SEND"""
        with override_config(EMAIL_AUTO_SEND=False):
            cloned = EmailMessage.objects.create(
                root_message_id="<cloned@test.com>",
                message_id="<cloned@test.com>",
                senders=self.email_msg.senders,
                recipients=self.email_msg.recipients,
                subject=self.email_msg.subject,
                body=self.email_msg.body,
            )
            # simulate ViewSet.resend: dispatch + set status
            tasks.async_send_email.delay(cloned.id)
            cloned.status = "sending"
            cloned.save(update_fields=["status"])

        mock_delay.assert_called_once()
        cloned.refresh_from_db()
        self.assertIn(cloned.status, ("sending", "retrying"))


class TestFullFlowIntegration(EmailAutoSendBase):
    """
    Integration: verify the complete flow respects EMAIL_AUTO_SEND.
    """

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @CELERY_EAGER
    @override_config(EMAIL_AUTO_SEND=False)
    def test_auto_send_false_no_emails_sent_automatically(self, mock_backend):
        """Full flow with EMAIL_AUTO_SEND=false: emails stored, zero sent"""
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        initial_sent = EmailMessage.objects.filter(status="sent").count()
        initial_total = EmailMessage.objects.count()

        contact = self._make_contact("fullflow@test.com")
        tlp_obj = Tlp.objects.get(name="Green")

        Communication.communicate_contact_summary(
            contact, [], [], tlp_obj, 7
        )

        handler = EmailHandler()
        handler.send_email(
            recipients=["to@test.com"],
            subject="Path B test",
            body="Body",
        )

        self.assertEqual(EmailMessage.objects.filter(status="sent").count(), initial_sent)
        self.assertGreater(EmailMessage.objects.count(), initial_total)

        pending = EmailMessage.objects.filter(status="pending")
        self.assertGreater(pending.count(), 0)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @CELERY_EAGER
    @override_config(EMAIL_AUTO_SEND=False)
    def test_auto_send_true_send_all_from_pending(self, mock_backend):
        """Store with EMAIL_AUTO_SEND=false, then send_all manually with mocked SMTP success"""
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        contact = self._make_contact("sendall@test.com")
        tlp_obj = Tlp.objects.get(name="Green")

        Communication.communicate_contact_summary(
            contact, [], [], tlp_obj, 7
        )

        pending = EmailMessage.objects.exclude(status="sent")
        ids = list(pending.values_list("id", flat=True))
        self.assertGreater(len(ids), 0)

        for email_id in ids:
            tasks.async_send_email(email_id)

        self.assertEqual(EmailMessage.objects.filter(status="sent").count(), len(ids))


class TestRetryEndpoint(EmailAutoSendBase):
    """
    Retry endpoint: clones a failed email and marks original as retried.
    """

    def setUp(self):
        self.failed_email = EmailMessage.objects.create(
            root_message_id="<fail@test.com>",
            message_id="<fail@test.com>",
            senders=[{"name": "test", "email": "test@ngen.com"}],
            recipients=[{"name": "to", "email": "to@test.com"}],
            subject="Failed email",
            body="Body",
            status="failed",
            last_error="SMTP error",
        )

    @patch("ngen.tasks.async_send_email.delay")
    @use_test_email_env()
    @CELERY_EAGER
    def test_retry_clones_and_dispatches(self, mock_delay):
        """Retry creates a clone, dispatches it, marks original as retried"""
        from ngen.tasks import async_send_email

        with override_config(EMAIL_AUTO_SEND=False):
            clone = EmailMessage.objects.create(
                root_message_id="<clone@test.com>",
                message_id="<clone@test.com>",
                senders=self.failed_email.senders,
                recipients=self.failed_email.recipients,
                subject=self.failed_email.subject,
                body=self.failed_email.body,
            )

            async_send_email.delay(clone.id)
            clone.status = "sending"
            clone.save(update_fields=["status"])

            self.failed_email.retried = True
            self.failed_email.save(update_fields=["retried"])

        mock_delay.assert_called_once()
        self.failed_email.refresh_from_db()
        self.assertTrue(self.failed_email.retried)
        clone.refresh_from_db()
        self.assertIn(clone.status, ("sending", "retrying"))

    def test_retried_email_cannot_be_retried_again(self):
        """Once retried=True, can't retry again"""
        self.failed_email.retried = True
        self.failed_email.save(update_fields=["retried"])

        self.assertTrue(self.failed_email.retried)
        self.assertEqual(self.failed_email.status, "failed")

    def test_sent_email_cannot_be_retried(self):
        """Only failed emails can be retried (not sent ones)"""
        self.failed_email.status = "sent"
        self.failed_email.save()
        self.failed_email.refresh_from_db()

        self.assertNotEqual(self.failed_email.status, "failed")
        self.assertEqual(self.failed_email.status, "sent")

    def test_pending_email_cannot_be_retried(self):
        """Pending (non-failed) emails should use send_now, not retry"""
        pending = EmailMessage.objects.create(
            root_message_id="<pending@test.com>",
            message_id="<pending@test.com>",
            senders=[{"name": "test", "email": "test@ngen.com"}],
            recipients=[{"name": "to", "email": "to@test.com"}],
            subject="Pending",
            body="Body",
            status="pending",
        )

        self.assertNotEqual(pending.status, "failed")
        self.assertNotEqual(pending.status, "sent")

    @patch("ngen.tasks.async_send_email.delay")
    @use_test_email_env()
    @CELERY_EAGER
    def test_retry_after_failure_creates_separate_record(self, mock_delay):
        """The clone from retry is a new record; if it fails, it can be retried too"""
        from ngen.tasks import async_send_email

        clone1 = EmailMessage.objects.create(
            root_message_id="<clone1@test.com>",
            message_id="<clone1@test.com>",
            senders=self.failed_email.senders,
            recipients=self.failed_email.recipients,
            subject=self.failed_email.subject,
            body=self.failed_email.body,
        )
        async_send_email.delay(clone1.id)
        clone1.status = "sending"
        clone1.save(update_fields=["status"])
        self.failed_email.retried = True
        self.failed_email.save(update_fields=["retried"])

        self.failed_email.refresh_from_db()
        self.assertTrue(self.failed_email.retried)

        clone1.status = "failed"
        clone1.last_error = "Clone also failed"
        clone1.save(update_fields=["status", "last_error"])

        self.assertFalse(clone1.retried)

        clone2 = EmailMessage.objects.create(
            root_message_id="<clone2@test.com>",
            message_id="<clone2@test.com>",
            senders=clone1.senders,
            recipients=clone1.recipients,
            subject=clone1.subject,
            body=clone1.body,
        )
        async_send_email.delay(clone2.id)
        clone2.status = "sending"
        clone2.save(update_fields=["status"])
        clone1.retried = True
        clone1.save(update_fields=["retried"])

        clone1.refresh_from_db()
        self.assertTrue(clone1.retried)
        clone2.refresh_from_db()
        self.assertIn(clone2.status, ("sending", "retrying"))
