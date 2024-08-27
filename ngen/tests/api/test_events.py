from datetime import timedelta

from django.urls import reverse
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


class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestEvent(APITestCaseWithLogin):
    """
    This will handle Event testcases
    """

    fixtures = [
        "priority.json",
        "feed.json",
        "tlp.json",
        "user.json",
        "taxonomy.json",
        "state.json",
        "edge.json",
        "report.json",
        "network_entity.json",
        "network.json",
        "contact.json",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            "notes": "estas son notas",
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
            priority_id=2,
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
