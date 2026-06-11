from constance.test import override_config
from django.test import TestCase, override_settings
from django.utils import timezone
from django.core import mail
from unittest.mock import patch, MagicMock

from ngen import tasks
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
    Playbook,
    Network,
    NetworkEntity,
    Task,
)
from ngen.models.email_message import EmailMessage
from ngen.tests.test_helpers import use_test_email_env

CELERY_EAGER = override_settings(CELERY_TASK_ALWAYS_EAGER=True)


class TasksTestCase(TestCase):
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
        "tests/playbook.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.priority = Priority.objects.get(name="High")
        cls.tlp = Tlp.objects.get(name="Green")
        cls.state = State.objects.get(name="Open")
        cls.case_template = CaseTemplate.objects.get(pk=1)
        cls.taxonomy = Taxonomy.objects.create(
            type="incident", name="Phising", slug="phising"
        )
        cls.feed = Feed.objects.get(slug="shodan", name="Shodan")
        cls.user = User.objects.create(
            username="test", password="test", priority=cls.priority
        )
        cls.contact = Contact.objects.get(pk=1)
        cls.network_entity = NetworkEntity.objects.get(pk=1)
        cls.network = Network.objects.get(pk=1)

        cls.playbook = Playbook.objects.get(pk=1)
        cls.task_obj = Task.objects.create(
            name="Test task",
            description="Test description",
            playbook=cls.playbook,
            priority=cls.priority,
        )

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


class TestAttendCases(TasksTestCase):
    def test_no_cases_to_attend(self):
        result = tasks.attend_cases()
        self.assertIsNone(result)

    @override_config(CASE_DEFAULT_LIFECYCLE="auto_open")
    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @CELERY_EAGER
    def test_case_with_auto_open_lifecycle(self, mock_backend):
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        case = self._create_case(lifecycle="auto_open")
        Case.objects.filter(pk=case.pk).update(
            created=timezone.now() - timezone.timedelta(minutes=60)
        )
        case.refresh_from_db()

        tasks.attend_cases()
        case.refresh_from_db()
        self.assertIsNotNone(case.attend_date)


class TestSolveCases(TasksTestCase):
    def test_no_cases_to_solve(self):
        result = tasks.solve_cases()
        self.assertIsNone(result)


class TestCaseRenotification(TasksTestCase):
    def test_no_cases_to_renotify(self):
        result = tasks.case_renotification()
        self.assertIsNone(result)


class TestContactSummary(TasksTestCase):
    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(NGEN_LANG="en")
    @CELERY_EAGER
    def test_contact_summary_with_email(self, mock_backend):
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        contact = Contact.objects.create(
            username="testuser@test.com",
            type="email",
            name="Test User",
            priority=self.priority,
        )

        self._create_case(lifecycle="manual")

        result = tasks.contact_summary(contact_usernames=["testuser@test.com"], days=7)
        self.assertIsNone(result)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @override_config(SUMMARY_TLP="none")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    @CELERY_EAGER
    def test_contact_summary_tlp_none(self, mock_backend):
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        result = tasks.contact_summary(contact_ids=[], days=7)
        self.assertIsNone(result)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(NGEN_LANG="en")
    @CELERY_EAGER
    def test_contact_summary_skips_contacts_without_cases(self, mock_backend):
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        Contact.objects.create(
            username="nocases@test.com",
            type="email",
            name="No Cases",
            priority=self.priority,
        )

        with self.assertLogs("ngen.tasks", level="INFO") as log_capture:
            tasks.contact_summary(contact_usernames=["nocases@test.com"], days=7)

        logged = "\n".join(log_capture.output)
        self.assertIn("skipped=1", logged)
        self.assertIn("sent=0", logged)


class TestCreateCasesForMatchingEvents(TasksTestCase):
    @CELERY_EAGER
    def test_no_matching_events(self):
        result = tasks.create_cases_for_matching_events(self.case_template.id)
        self.assertIsNone(result)


class TestExportEventsForEmailTask(TasksTestCase):
    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @override_config(SUMMARY_TLP="red")
    @override_config(TEAM_NAME="TEAM")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(NGEN_LANG="en")
    @CELERY_EAGER
    def test_contact_not_found(self, mock_backend):
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        result = tasks.export_events_for_email_task("nonexistent@test.com", days=7)
        self.assertEqual(result["status"], "error")


class TestRetestEventKintun(TasksTestCase):
    @CELERY_EAGER
    def test_event_not_found(self):
        result = tasks.retest_event_kintun(99999)
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)


class TestInternalAddressInfo(TasksTestCase):
    @CELERY_EAGER
    def test_domain_not_found(self):
        result = tasks.internal_address_info("nonexistent.domain.test")
        self.assertIsInstance(result, dict)
        self.assertIn("query", result)

    @CELERY_EAGER
    def test_ip_not_found(self):
        result = tasks.internal_address_info("192.168.255.255")
        self.assertIsInstance(result, dict)


class TestWhoisLookup(TasksTestCase):
    @CELERY_EAGER
    def test_basic_lookup(self):
        result = tasks.whois_lookup("8.8.8.8")
        self.assertIsInstance(result, dict)
        self.assertIn("ngen", result)


class TestAsyncSendEmail(TasksTestCase):
    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @CELERY_EAGER
    def test_no_email_message_id(self, mock_backend):
        result = tasks.async_send_email(0)
        self.assertEqual(result["status"], "error")

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @CELERY_EAGER
    def test_email_message_not_found(self, mock_backend):
        with self.assertRaises(Exception):
            tasks.async_send_email(99999)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @CELERY_EAGER
    def test_send_email_success(self, mock_backend):
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        email_message = EmailMessage.objects.create(
            root_message_id="<test@ngen.com>",
            message_id="<test@ngen.com>",
            senders=[{"name": "test", "email": "test@ngen.com"}],
            recipients=[{"name": "to", "email": "to@test.com"}],
            subject="Test subject",
            body="Test body",
        )

        result = tasks.async_send_email(email_message.id)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(mail.outbox), 1)

    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @CELERY_EAGER
    @patch("ngen.tasks.async_send_email.retry")
    def test_send_failure_triggers_retry(self, mock_retry, mock_backend):
        mock_conn = MagicMock()
        mock_conn.send_messages.side_effect = Exception("SMTP error")
        mock_backend.return_value = mock_conn

        email_message = EmailMessage.objects.create(
            root_message_id="<fail@ngen.com>",
            message_id="<fail@ngen.com>",
            senders=[{"name": "test", "email": "test@ngen.com"}],
            recipients=[{"name": "to", "email": "to@test.com"}],
            subject="Fail test",
            body="Test body",
        )

        tasks.async_send_email(email_message.id)
        email_message.refresh_from_db()
        self.assertTrue(email_message.send_attempt_failed)
        self.assertIsNotNone(email_message.last_error)
        mock_retry.assert_called_once()


class TestRetrieveEmails(TasksTestCase):
    def test_no_config_returns_error(self):
        with override_config(EMAIL_HOST=None):
            result = tasks.retrieve_emails()
            self.assertEqual(result["status"], "error")

    @use_test_email_env()
    @patch("ngen.tasks.EmailClient")
    def test_connection_refused_handled(self, mock_client):
        mock_client.side_effect = ConnectionRefusedError("refused")
        result = tasks.retrieve_emails()
        self.assertIsNone(result)

    @use_test_email_env()
    @patch("ngen.tasks.EmailClient")
    def test_timeout_handled(self, mock_client):
        mock_client.side_effect = TimeoutError("timed out")
        result = tasks.retrieve_emails()
        self.assertIsNone(result)


class TestSendContactChecks(TasksTestCase):
    @CELERY_EAGER
    def test_no_frontend_url(self):
        with override_config(FRONTEND_PUBLIC_URL=None):
            result = tasks.send_contact_checks()
            self.assertIsNone(result)  # ignore_result=True en eager mode

    @override_config(FRONTEND_PUBLIC_URL="http://test.com")
    @CELERY_EAGER
    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    def test_sends_contact_checks(self, mock_backend):
        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        Contact.objects.create(
            username="check@test.com",
            type="email",
            name="Check User",
            priority=self.priority,
        )

        result = tasks.send_contact_checks()
        self.assertIsNone(result)


class TestSendContactCheckReminder(TasksTestCase):
    @CELERY_EAGER
    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @override_config(FRONTEND_PUBLIC_URL="http://test.com")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    def test_sends_reminder(self, mock_backend):
        from ngen.models.constituency import ContactCheck

        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        contact = Contact.objects.create(
            username="reminder@test.com",
            type="email",
            name="Reminder",
            priority=self.priority,
        )
        check = ContactCheck.objects.create(contact=contact)

        result = tasks.send_contact_check_reminder(check.id)
        self.assertIsNone(result)


class TestSendContactCheckSubmitted(TasksTestCase):
    @CELERY_EAGER
    @patch("ngen.tasks.EmailBackend")
    @use_test_email_env()
    @override_config(EMAIL_AUTO_SEND=True)
    @override_config(FRONTEND_PUBLIC_URL="http://test.com")
    @override_config(TEAM_EMAIL="team@ngen.com")
    @override_config(TEAM_NAME="TEAM")
    @override_config(NGEN_LANG="en")
    def test_sends_submitted(self, mock_backend):
        from ngen.models.constituency import ContactCheck

        mock_backend.return_value = mail.get_connection(
            "django.core.mail.backends.locmem.EmailBackend"
        )

        contact = Contact.objects.create(
            username="submitted@test.com",
            type="email",
            name="Submitted",
            priority=self.priority,
        )
        check = ContactCheck.objects.create(contact=contact)

        result = tasks.send_contact_check_submitted(check.id)
        self.assertIsNone(result)


class TestGetAffectedContactsAndCommunicate(TasksTestCase):
    @CELERY_EAGER
    def test_no_external_contacts(self):
        case = self._create_case(lifecycle="manual")

        result = tasks.get_affected_contacts_and_communicate_event(
            self.event.id,
            "case_report",
            {},
            False,
        )
        self.assertIsNone(result)
