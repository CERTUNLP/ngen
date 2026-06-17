from datetime import timedelta

from django.urls import reverse
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from ngen.models.email_message import EmailMessage
from ngen.models.state import State
from rest_framework import status
from rest_framework_simplejwt.tokens import Token

from ngen.models import (
    Event,
    Case,
    CaseTemplate,
    Taxonomy,
    Priority,
    Tlp,
    User,
    Feed,
    Artifact,
)
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin
from ngen.tests.test_helpers import use_test_email_env
from constance.test import override_config


class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestEvent(APITestCaseWithLogin):
    """
    This will handle Event testcases
    """

    fixtures = [
        "tests/priority.json",
        "tests/feed.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/taxonomy.json",
        "tests/state.json",
        "tests/edge.json",
        "tests/report.json",
        "tests/network_entity.json",
        "tests/network.json",
        "tests/contact.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        basename = "event"
        cls.url_list = reverse(f"{basename}-list")
        cls.url_detail = lambda pk: reverse(f"{basename}-detail", kwargs={"pk": pk})
        cls.url_login_jwt = reverse("token-create")
        cls.json_login = {"username": "ngen", "password": "ngen"}

        cls.base_url = "http://testserver"
        cls.priority_url = cls.base_url + reverse(
            "priority-detail", kwargs={"pk": 2}
        )  # 'high'
        cls.tlp_url = cls.base_url + reverse("tlp-detail", kwargs={"pk": 2})  # 'amber'
        cls.taxonomy_url = cls.base_url + reverse(
            "taxonomy-detail", kwargs={"pk": 42}
        )  # 'copyright'
        cls.feed_url = cls.base_url + reverse("feed-detail", kwargs={"pk": 1})

        cls.priority = Priority.objects.get(slug="high")
        cls.taxonomy = Taxonomy.objects.get(slug="copyright")
        cls.feed = Feed.objects.get(slug="csirtamericas")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.user = User.objects.get(username="ngen")

    def test_event_get_list(self):
        """
        This will test successful Event GET list
        """

        events = [
            Event.objects.create(
                domain="info.unlp.edu.ar",
                taxonomy=self.taxonomy,
                feed=self.feed,
                tlp=self.tlp,
                reporter=self.user,
                notes="Some notes",
                priority=self.priority,
            ),
            Event.objects.create(
                domain="*",
                taxonomy=self.taxonomy,
                feed=self.feed,
                tlp=self.tlp,
                reporter=self.user,
                notes="Some notes",
                priority=self.priority,
            ),
        ]

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(events))

    def test_event_get_detail(self):
        """
        This will test successful Event GET detail
        """

        event = Event.objects.create(
            domain="*",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )

        response = self.client.get(self.url_detail(event.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_post_with_cidr(self):
        """
        This will test successfull Event POST
        """
        json_data = {
            "cidr": "2.2.2.2",
            # 'domain': 'bbb',
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_post_with_domain(self):
        """
        This will test successfull Event POST
        """
        json_data = {
            # 'cidr': '2.2.2.2',
            "domain": "info.unlp.edu.ar",
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_post_domain_artifact_creation(self):
        """
        This will test successfull Event POST
        """
        json_data = {
            # 'cidr': '2.2.2.2',
            "domain": "info.unlp.edu.ar",
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        artifacts = Event.objects.last().artifacts
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].related[0], Event.objects.last())
        self.assertEqual(artifacts[0].value, "info.unlp.edu.ar")

    def test_event_post_cidr_artifact_creation(self):
        """
        This will test successfull Event POST
        """
        json_data = {
            "cidr": "2.2.2.2",
            # 'domain': 'info.unlp.edu.ar',
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        artifacts = Event.objects.last().artifacts
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].related[0], Event.objects.last())
        self.assertEqual(artifacts[0].value, "2.2.2.2")

    def test_event_post_with_slugs(self):
        """
        This will test successfull Event POST
        """
        json_data = {
            # 'cidr': '2.2.2.2',
            "domain": "info.unlp.edu.ar",
            "notes": "these are notes",
            "priority": "critical",
            "tlp": "amber",
            "taxonomy": "phishing",
            "feed": "shodan",
        }

        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_post_with_cidr_and_domain(self):
        """
        This will test bad request Event POST
        """
        json_data = {
            "cidr": "2.2.2.2",
            "domain": "info.unlp.edu.ar",
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_with_cidr_null_and_domain_null(self):
        """
        This will test bad request Event POST
        """
        json_data = {
            # 'cidr': '',
            # 'domain': 'info.unlp.edu.ar',
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_with_cidr_empty_and_domain_null(self):
        """
        This will test bad request Event POST
        """
        json_data = {
            "cidr": "",
            # 'domain': 'info.unlp.edu.ar',
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_with_cidr_null_and_domain_empty(self):
        """
        This will test successfull Event POST
        """
        json_data = {
            # 'cidr': '',
            "domain": "",
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_with_cidr_empty_and_domain_empty(self):
        """
        This will test successfull Event POST
        """
        json_data = {
            "cidr": "",
            "domain": "",
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_with_cidr_wildcard_and_domain_empty(self):
        """
        This will test bad request Event POST
        """
        json_data = {
            "cidr": "0.0.0.0/0",
            "domain": "",
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_post_with_cidr_wildcard_and_domain_wildcard(self):
        """
        This will test bad request Event POST
        """
        json_data = {
            "cidr": "0.0.0.0/0",
            "domain": "*",
            "notes": "these are notes",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_post_fields_not_editable(self):
        """
        This will test successfull Event POST
        """
        pass  # TODO

    def test_event_post_that_matches_with_case_template(self):
        """
        This will test a successful Event POST that matches with a Case Template,
        therefore creating a Case
        """

        initial_case_count = Case.objects.count()

        case_template = CaseTemplate.objects.create(
            case_priority_id=2,
            cidr=None,
            domain="*",
            event_taxonomy_id=91,
            event_feed_id=11,
            case_tlp_id=4,
            case_state_id=3,
            case_lifecycle="auto_open",
            active=True,
        )

        json_data = {
            "domain": "info.unlp.edu.ar",
            "notes": "Some notes",
            "priority": "critical",
            "tlp": "amber",
            "taxonomy": "phishing",
            "feed": "shodan",
        }

        response = self.client.post(self.url_list, data=json_data)
        new_case_count = Case.objects.count()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["case"],
            self.base_url
            + reverse("case-detail", kwargs={"pk": Case.objects.last().pk}),
        )
        self.assertEqual(new_case_count, initial_case_count + 1)
        self.assertEqual(Event.objects.last().case, Case.objects.last())
        self.assertEqual(Case.objects.last().casetemplate_creator, case_template)

    def test_event_patch(self):
        """
        This will test successful Event PATCH
        """

        event = Event.objects.create(
            domain="*",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )

        another_priority_url = self.base_url + reverse(
            "priority-detail", kwargs={"pk": 1}
        )

        json_data = {
            "priority": another_priority_url,
            "domain": "another.domain.com",
            "artifact": event.artifacts[0],
        }

        response = self.client.patch(self.url_detail(event.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_put_without_case(self):
        case = Case.objects.create(
            priority=self.priority, tlp=self.tlp,
            state=State.objects.get(pk=3),
        )
        event = Event.objects.create(
            domain="unlink.test.com", priority=self.priority,
            taxonomy=self.taxonomy, feed=self.feed, tlp=self.tlp, reporter=self.user,
            case=case,
        )

        json_data = {
            "domain": "unlink.test.com", "notes": "unlinked",
            "priority": self.priority_url, "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url, "feed": self.feed_url,
            "reporter": self.base_url + reverse("user-detail", kwargs={"pk": self.user.pk}),
            "case": "",
        }
        response = self.client.put(self.url_detail(event.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        event.refresh_from_db()
        self.assertIsNone(event.case)

    def test_event_patch_clear_case(self):
        case = Case.objects.create(
            priority=self.priority, tlp=self.tlp,
            state=State.objects.get(pk=3),
        )
        event = Event.objects.create(
            domain="patch-unlink.test.com", priority=self.priority,
            taxonomy=self.taxonomy, feed=self.feed, tlp=self.tlp, reporter=self.user,
            case=case,
        )

        json_data = {"case": None}
        response = self.client.patch(self.url_detail(event.pk), data=json_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        event.refresh_from_db()
        self.assertIsNone(event.case)

    def test_event_put_same_automatic_artifact(self):
        """
        This will test successful Event PUT
        """

        event = Event.objects.create(
            domain="*",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )

        actual_artifact = self.base_url + reverse(
            "artifact-detail", kwargs={"pk": event.artifacts[0].pk}
        )

        json_data = {
            "domain": "another.domain3.com",
            "notes": "Some notes",
            "priority": "low",
            "tlp": "amber",
            "taxonomy": "phishing",
            "feed": "shodan",
            "artifacts": [actual_artifact],
        }

        response = self.client.put(self.url_detail(event.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        artifacts = Event.objects.last().artifacts
        self.assertEqual(len(artifacts), 2)
        self.assertEqual(artifacts[0].related[0], Event.objects.last())
        self.assertEqual(artifacts[1].related[0], Event.objects.last())
        self.assertIn("*", [artifact.value for artifact in artifacts])
        self.assertIn("another.domain3.com", [artifact.value for artifact in artifacts])

    def test_event_put_another_manual_artifact(self):
        """
        This will test successful Event PUT
        """

        event = Event.objects.create(
            domain="*",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )

        other_artifact = Artifact.objects.create(value="another.domain5.com")
        other_artifact_url = self.base_url + reverse(
            "artifact-detail", kwargs={"pk": other_artifact.pk}
        )

        json_data = {
            "domain": "another.domain3.com",
            "notes": "Some notes",
            "priority": "low",
            "tlp": "amber",
            "taxonomy": "phishing",
            "feed": "shodan",
            "artifacts": [other_artifact_url],
        }

        response = self.client.put(self.url_detail(event.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        artifacts = Event.objects.last().artifacts
        self.assertEqual(len(artifacts), 2)
        self.assertEqual(artifacts[0].related[0], Event.objects.last())
        self.assertIn("another.domain3.com", [artifact.value for artifact in artifacts])
        self.assertIn("another.domain5.com", [artifact.value for artifact in artifacts])

    def test_event_delete(self):
        """
        This will test successful Event DELETE
        """

        event = Event.objects.create(
            domain="*",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )
        event_pk = event.pk

        response = self.client.delete(self.url_detail(event_pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Case.DoesNotExist):
            Case.objects.get(pk=event_pk)

    @use_test_email_env()
    @override_config(CASE_REPORT_NEW_CASES=True)
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_event_post_with_evidence(self):
        """
        This will test successful Event POST with an evidence file attached
        """
        initial_count = EmailMessage.objects.count()

        # Create the new evidence file to upload
        evidence_file = SimpleUploadedFile(
            "file.txt", b"file_content", content_type="text/plain"
        )

        json_data = {
            "address_value": "1.11.13.14",
            "notes": "test",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
            "avoid_auto_merge": "false",
            "evidence": evidence_file,  # Pass the simulated file
        }

        # Using format='multipart' is required so DRF handles form-data correctly
        response = self.client.post(self.url_list, data=json_data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Validate that the event was created
        created_event = Event.objects.last()
        self.assertIsNotNone(created_event)

        self.assertEqual(EmailMessage.objects.count(), initial_count)
        # NOTE: Depending on how your model stores evidence
        # (e.g., a FileField on Event or a related model), you can add an assertion here.
        # For example: self.assertTrue(created_event.evidences.exists())

    @use_test_email_env()
    @override_config(CASE_REPORT_NEW_CASES=True)
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_event_put_add_evidence(self):
        """
        This will test successful Event PUT adding an extra evidence file
        """
        initial_count = EmailMessage.objects.count()

        # Create the new evidence file to upload
        new_evidence_file = SimpleUploadedFile(
            "file2.txt", b"file_content2", content_type="text/plain"
        )
        ef1_sha1 = "2196496b4e89e354291719e76978ac7540d7adf5"

        # Prepare the payload used to create the initial event
        json_data = {
            "date": "2026-04-28T13:43",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
            "address_value": "test.com",
            "avoid_auto_merge": "true",
            "evidence": new_evidence_file,
        }

        # Create the initial event using multipart form data
        response = self.client.post(self.url_list, data=json_data, format="multipart")
        event_uuid = response.data["uuid"]
        event_id = response.data["url"].split("/")[-2]

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(EmailMessage.objects.count(), initial_count)

        # Create a case and assign the event to it
        self.case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            state=State.objects.get(name="Open"),
        )
        self.assertEqual(EmailMessage.objects.count(), initial_count + 1)

        event = Event.objects.get(pk=event_id)
        event.case = self.case
        event.save()

        self.assertEqual(EmailMessage.objects.count(), initial_count + 3)
        all_emails = EmailMessage.objects.all()
        email_with_attachment = None
        for email in all_emails:
            if email.attachments and len(email.attachments) > 0:
                email_with_attachment = email
                break
        self.assertIsNotNone(email_with_attachment)
        self.assertEqual(len(email_with_attachment.attachments), 1)
        first_attachment = email_with_attachment.attachments[0]
        self.assertIn(ef1_sha1, first_attachment["name"])

        # Add a new evidence file to the event
        another_evidence_file = SimpleUploadedFile(
            "file3.txt", b"file_content3", content_type="text/plain"
        )
        ef2_sha1 = "676640c7903a09368d69757973d15848930c64a1"
        json_data_update = {
            "date": "2026-04-28T13:43",
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "taxonomy": self.taxonomy_url,
            "feed": self.feed_url,
            "address_value": "test.com",
            "avoid_auto_merge": "true",
            "evidence": another_evidence_file,
        }
        response_update = self.client.put(
            self.url_detail(event_id), data=json_data_update, format="multipart"
        )
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)

        # Verify that an email was sent after adding the new evidence and that it includes the attachment
        self.assertEqual(EmailMessage.objects.count(), initial_count + 5)

        last_email = EmailMessage.objects.first()
        self.assertEqual(len(last_email.attachments), 2)
        second_attachment = last_email.attachments[1]
        first_attachment = last_email.attachments[0]
        self.assertIn(ef1_sha1, first_attachment["name"])
        self.assertIn(ef2_sha1, second_attachment["name"])
        self.assertIn(event_uuid, first_attachment["name"])
        self.assertIn(event_uuid, second_attachment["name"])
