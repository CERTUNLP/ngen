from django.urls import reverse
from rest_framework import status
from django.test import override_settings

from ngen.models import (
    Case,
    Priority,
    Tlp,
    State,
    CaseTemplate,
    Event,
    Taxonomy,
    Feed,
    User,
    Network,
    Contact,
    NetworkEntity,
)
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin
from ngen.tests.test_helpers import use_test_email_env


class TestCase(APITestCaseWithLogin):
    """
    This will handle Case testcases
    """

    fixtures = [
        "tests/contact.json",
        "tests/priority.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/state.json",
        "tests/feed.json",
        "tests/taxonomy.json",
        "tests/case_template.json",
        "tests/user.json",
        "tests/network_entity.json",
        "tests/edge.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        basename = "case"
        cls.url_list = reverse(f"{basename}-list")
        cls.url_detail = lambda pk: reverse(f"{basename}-detail", kwargs={"pk": pk})

        cls.url_login_jwt = reverse("token-create")
        cls.json_login = {"username": "ngen", "password": "ngen"}

        cls.base_url = "http://testserver"
        cls.priority_url = cls.base_url + reverse(
            "priority-detail", kwargs={"pk": 2}
        )  # 'high'
        cls.tlp_url = cls.base_url + reverse("tlp-detail", kwargs={"pk": 2})  # 'amber'
        cls.state_url = cls.base_url + reverse("state-detail", kwargs={"pk": 3})  # open
        cls.case_template_url = cls.base_url + reverse(
            "casetemplate-detail", kwargs={"pk": 1}
        )

        cls.priority = Priority.objects.get(slug="high")
        cls.feed = Feed.objects.get(slug="csirtamericas")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.state = State.objects.get(slug="open")
        cls.taxonomy = Taxonomy.objects.get(slug="accessible_afp_report")
        cls.user = User.objects.get(username="ngen")
        cls.case_template = CaseTemplate.objects.get(pk=1)
        cls.domain = "test.com"
        cls.contact = Contact.objects.get(pk=1)
        cls.network_entity = NetworkEntity.objects.get(pk=1)

        cls.network = Network.objects.create(
            domain=cls.domain,
            active=True,
            type="external",
            network_entity=cls.network_entity,
        )
        cls.network.contacts.set([cls.contact])

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_get_list(self):
        """
        This will test successful Case GET list
        """

        cases = [
            Case.objects.create(
                priority=self.priority,
                tlp=self.tlp,
                casetemplate_creator=self.case_template,
                state=self.state,
            ),
            Case.objects.create(
                priority=self.priority,
                tlp=self.tlp,
                casetemplate_creator=self.case_template,
                state=self.state,
            ),
        ]

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(cases))

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_get_detail(self):
        """
        This will test successful Case GET detail
        """

        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state,
        )

        response = self.client.get(self.url_detail(case.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_post_with_valid_events(self):
        """
        This will test successful Case POST
        """

        event = Event.objects.create(
            domain=self.domain,
            priority=self.priority,
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
        )
        event_url = self.base_url + reverse("event-detail", kwargs={"pk": event.pk})

        json_data = {
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "state": self.state_url,
            "casetemplate_creator": self.case_template_url,
            "events": [event_url],
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_post_with_empty_events(self):
        """
        This will test successful Case POST
        """

        json_data = {
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "state": self.state_url,
            "casetemplate_creator": self.case_template_url,
            "events": [],
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_post_with_invalid_events(self):
        """
        This will test successful Case POST
        """

        json_data = {
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "state": self.state_url,
            "casetemplate_creator": self.case_template_url,
            "events": ["http://testserver/event/123123/"],
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_patch(self):
        """
        This will test successful Case PATCH
        """

        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state,
        )

        another_priority_url = self.base_url + reverse(
            "priority-detail", kwargs={"pk": 1}
        )

        json_data = {"priority": another_priority_url}

        response = self.client.patch(self.url_detail(case.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _case_with_tags(self):
        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state,
        )
        case.tags.set(["urgent", "phishing"])
        return case

    def test_case_patch_keeps_the_tags(self):
        """
        This will test that a partial update that does not mention the tags
        leaves them alone, which is what closing a case from the list does
        """
        case = self._case_with_tags()
        closed = State.objects.filter(solved=True).first()

        response = self.client.patch(
            self.url_detail(case.pk),
            data={
                "state": self.base_url
                + reverse("state-detail", kwargs={"pk": closed.pk})
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(response.data["tags"], ["urgent", "phishing"])
        self.assertCountEqual(
            case.tags.names(),
            ["urgent", "phishing"],
        )

    def test_case_patch_changes_the_tags_when_they_are_sent(self):
        """
        This will test that the tags are still updated when the request carries
        them
        """
        case = self._case_with_tags()

        response = self.client.patch(
            self.url_detail(case.pk), data={"tags": ["only-this-one"]}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(case.tags.names(), ["only-this-one"])

    def test_case_patch_can_empty_the_tags(self):
        """
        This will test that asking for no tags does empty them, which is not
        the same as not mentioning them
        """
        case = self._case_with_tags()

        response = self.client.patch(
            self.url_detail(case.pk), data={"tags": []}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(case.tags.names()), [])

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_put_without_tags_keeps_them(self):
        """
        This will test that a full update that does not carry the tags leaves
        them alone, the same as a partial one: a form field with no value is
        not sent at all, so an absent field cannot mean 'delete them'
        """
        case = self._case_with_tags()

        response = self.client.put(
            self.url_detail(case.pk),
            data={
                "priority": self.priority_url,
                "tlp": self.tlp_url,
                "state": self.state_url,
                "casetemplate_creator": self.case_template_url,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(case.tags.names(), ["urgent", "phishing"])

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_put_can_empty_the_tags(self):
        """
        This will test the way the case form empties the tags: since an empty
        list cannot be sent as form data, it sends an explicit empty one
        """
        case = self._case_with_tags()

        response = self.client.put(
            self.url_detail(case.pk),
            data={
                "priority": self.priority_url,
                "tlp": self.tlp_url,
                "state": self.state_url,
                "casetemplate_creator": self.case_template_url,
                "tags": "[]",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(list(case.tags.names()), [])

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_put(self):
        """
        This will test successful Case PUT
        """

        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state,
        )

        another_priority_url = self.base_url + reverse(
            "priority-detail", kwargs={"pk": 1}
        )

        json_data = {
            "priority": another_priority_url,
            "tlp": self.tlp_url,
            "state": self.state_url,
            "casetemplate_creator": self.case_template_url,
        }

        response = self.client.put(self.url_detail(case.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_put_unlinks_removed_events(self):
        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state,
        )
        event1 = Event.objects.create(
            domain="a.test.com",
            priority=self.priority,
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            case=case,
        )
        event2 = Event.objects.create(
            domain="b.test.com",
            priority=self.priority,
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            case=case,
        )
        event3 = Event.objects.create(
            domain="c.test.com",
            priority=self.priority,
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            case=case,
        )

        event1_url = self.base_url + reverse("event-detail", kwargs={"pk": event1.pk})
        event2_url = self.base_url + reverse("event-detail", kwargs={"pk": event2.pk})

        json_data = {
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "state": self.state_url,
            "casetemplate_creator": self.case_template_url,
            "events": [event1_url, event2_url],
        }
        response = self.client.put(self.url_detail(case.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        event3.refresh_from_db()
        self.assertIsNone(event3.case)
        event1.refresh_from_db()
        self.assertEqual(event1.case, case)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_put_empty_events_unlinks_all(self):
        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state,
        )
        event = Event.objects.create(
            domain="d.test.com",
            priority=self.priority,
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            case=case,
        )

        json_data = {
            "priority": self.priority_url,
            "tlp": self.tlp_url,
            "state": self.state_url,
            "casetemplate_creator": self.case_template_url,
            "events": [],
        }
        response = self.client.put(self.url_detail(case.pk), data=json_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        event.refresh_from_db()
        self.assertIsNone(event.case)

    @use_test_email_env()
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_case_delete(self):
        """
        This will test successful Case DELETE
        """

        case = Case.objects.create(
            priority=self.priority,
            tlp=self.tlp,
            casetemplate_creator=self.case_template,
            state=self.state,
        )
        case_pk = case.pk

        response = self.client.delete(self.url_detail(case_pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Case.DoesNotExist):
            Case.objects.get(pk=case_pk)
