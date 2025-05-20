"""
Django Unit Tests for EmailMessage model
"""

from django.test import TestCase  # type: ignore
from django.utils import timezone  # type: ignore

from ngen.models import EmailMessage
from ngen.models.taxonomy import Report, Taxonomy


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
                {"name": "Another Victim Name", "email": "another_victim@university.com"}
            ],
            date=timezone.now(),
            body="some body",
            sent=True,
            send_attempt_failed=False,
        )

        # Setup for taxonomies and reports
        cls.abuelo = Taxonomy.objects.create(name="Abuelo", type="incident")
        cls.padre = Taxonomy.objects.create(name="Padre", type="incident", parent=cls.abuelo)
        cls.hijo = Taxonomy.objects.create(name="Hijo", type="incident", parent=cls.padre)

        cls.reporte_abuelo = Report.objects.create(
            taxonomy=cls.abuelo, lang="es", problem="Reporte abuelo"
        )
        cls.reporte_padre = Report.objects.create(
            taxonomy=cls.padre, lang="en", problem="Parent report"
        )

    def test_email_message_creation(self):
        """
        This will test EmailMessage creation
        """
        self.assertIsInstance(self.root_email_message, EmailMessage)
        self.assertIsInstance(self.email_message_2, EmailMessage)
        self.assertIsInstance(self.email_message_3, EmailMessage)
        self.assertIsInstance(self.email_message_4, EmailMessage)

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

        self.assertQuerysetEqual(email_messages, expected_messages, transform=lambda x: x)

        non_existent = EmailMessage.get_message_thread_by("non-existent")
        self.assertEqual(non_existent.count(), 0)

    def test_uses_parent_report_if_available(self):
        """
        Verifies that if the parent has a report in the requested language, it is used.
        """
        report = self.hijo.get_matching_report(lang="en")
        self.assertEqual(report[0], self.reporte_padre)

    def test_does_not_use_parent_report_if_different_language(self):
        """
        Verifies that the parent's report is not used if it is in a different language.
        """
        report = self.hijo.get_matching_report(lang="es")
        self.assertEqual(report[0], self.reporte_abuelo)

    def test_returns_empty_if_no_reports_in_language(self):
        """
        Verifies that if no one in the hierarchy has a report in the requested language, it returns empty.
        """
        report = self.hijo.get_matching_report(lang="fr")
        self.assertEqual(report, [])

    def test_uses_own_report_if_available(self):
        """
        Verifies that if the node itself has a report in the language, it is used instead of the parent's.
        """
        own_report = Report.objects.create(
            taxonomy=self.hijo, lang="es", problem="Soy yo"
        )
        report = self.hijo.get_matching_report(lang="es")
        self.assertEqual(report[0], own_report)

    def test_get_message_thread_by_ignores_invalid_messages(self):
        """
        Verifies that messages with None as root_message_id are not returned in threads.
        """
        bad_message = EmailMessage.objects.create(
            root_message_id=None,
            parent_message_id=None,
            message_id="<bad@cert.unlp.edu.ar>",
            references=[],
            subject="Broken",
            senders=[],
            recipients=[],
            date=timezone.now(),
            body="bad",
            sent=False,
            send_attempt_failed=True,
        )
        result = EmailMessage.get_message_thread_by("non-existent-id")
        self.assertNotIn(bad_message, result)

    def test_email_message_references_chain(self):
        """
        Verifies that the references field contains the expected message chain.
        """
        expected_refs = [
            "<172654248025.81.10116784141945641235@cert.unlp.edu.ar>",
            "<172654293755.81.289851525536098366@cert.unlp.edu.ar>",
        ]
        self.assertEqual(self.email_message_3.references, expected_refs)

    def test_get_message_thread_by_returns_empty_for_unknown_id(self):
        """
        Ensures that querying a thread with a non-existent message ID returns an empty queryset.
        """
        result = EmailMessage.get_message_thread_by("non-existent-id")
        self.assertEqual(result.count(), 0)

    def test_email_message_sent_flags(self):
        """
        Tests the sent and send_attempt_failed flags are correctly set on creation.
        """
        self.assertTrue(self.root_email_message.sent)
        self.assertFalse(self.root_email_message.send_attempt_failed)

    def test_message_thread_ordering(self):
        """
        Ensures that messages returned in a thread are in the expected order.
        """
        messages = EmailMessage.get_message_thread_by(
            self.root_email_message.message_id
        )
        self.assertEqual(
            [m.message_id for m in messages],
            [
                self.root_email_message.message_id,
                self.email_message_2.message_id,
                self.email_message_3.message_id,
            ],
        )
