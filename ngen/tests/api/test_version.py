from django.test import override_settings
from django.utils import timezone

from ngen.models import EmailMessage
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin
from ngen.tests.test_helpers import use_test_email_env


class TestVersionEndpoint(APITestCaseWithLogin):
    fixtures = [
        "tests/priority.json",
        "tests/user.json",
        "tests/taxonomy.json",
        "tests/feed.json",
        "tests/tlp.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = "/api/version/"

    def _make_email(self, **kwargs):
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

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_version_returns_200_and_includes_email_queue(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("email_queue", response.data)
        self.assertIn("pending", response.data["email_queue"])
        self.assertIn("sent_total", response.data["email_queue"])
        self.assertIn("failed", response.data["email_queue"])
        self.assertIn("total", response.data["email_queue"])
        self.assertIn("auto_send", response.data["email_queue"])

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_version_email_queue_counts_match_database(self):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        self._make_email(
            status=EmailMessage.Status.PENDING,
            root_message_id="<p1@t.com>", message_id="<p1@t.com>",
        )
        self._make_email(
            status=EmailMessage.Status.PENDING,
            root_message_id="<p2@t.com>", message_id="<p2@t.com>",
        )
        self._make_email(
            status=EmailMessage.Status.SENT, date=timezone.now(),
            root_message_id="<s1@t.com>", message_id="<s1@t.com>",
        )
        self._make_email(
            status=EmailMessage.Status.FAILED,
            root_message_id="<f1@t.com>", message_id="<f1@t.com>",
        )
        self._make_email(
            status=EmailMessage.Status.SENDING,
            root_message_id="<d1@t.com>", message_id="<d1@t.com>",
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        eq = response.data["email_queue"]
        self.assertEqual(eq["pending"], 2)
        self.assertEqual(eq["sent_today"], 1)
        self.assertEqual(eq["sent_total"], 1)
        self.assertEqual(eq["failed"], 1)
        self.assertEqual(eq["total"], 5)
