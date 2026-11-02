from django.urls import reverse
from rest_framework import status

from ngen.models import (
    Case,
    Event,
    Feed,
    Priority,
    State,
    Taxonomy,
    Tlp,
    User,
)
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin


class TestExactSearch(APITestCaseWithLogin):
    """
    Literal search mode (?search_mode=exact) of NgenSearchFilter
    """

    fixtures = [
        "tests/priority.json",
        "tests/feed.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/taxonomy.json",
        "tests/state.json",
        "tests/edge.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_events = reverse("event-list")
        cls.url_cases = reverse("case-list")
        cls.url_taxonomies = reverse("taxonomy-list")

        cls.priority = Priority.objects.get(slug="high")
        cls.taxonomy = Taxonomy.objects.get(slug="copyright")
        cls.feed = Feed.objects.get(slug="csirtamericas")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.user = User.objects.get(username="ngen")
        cls.state = State.objects.get(pk=1)

        cls.event_ip = cls.create_event(address_value="163.10.34.15")
        cls.event_ip_longer = cls.create_event(address_value="163.10.34.155")
        cls.event_network = cls.create_event(address_value="163.10.34.0/24")
        cls.event_domain = cls.create_event(address_value="unlp.edu.ar")
        cls.event_subdomain = cls.create_event(address_value="info.unlp.edu.ar")

        cls.case_ip = Case.objects.create(
            priority=cls.priority, tlp=cls.tlp, state=cls.state
        )
        cls.case_ip_longer = Case.objects.create(
            priority=cls.priority, tlp=cls.tlp, state=cls.state
        )
        Event.objects.filter(pk=cls.event_ip.pk).update(case=cls.case_ip)
        Event.objects.filter(pk=cls.event_ip_longer.pk).update(case=cls.case_ip_longer)

    @classmethod
    def create_event(cls, **address):
        return Event.objects.create(
            taxonomy=cls.taxonomy,
            feed=cls.feed,
            tlp=cls.tlp,
            reporter=cls.user,
            priority=cls.priority,
            **address,
        )

    def search_ids(self, url, term, exact=True):
        params = {"search": term}
        if exact:
            params["search_mode"] = "exact"
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return {item["url"].rstrip("/").rsplit("/", 1)[-1] for item in response.data["results"]}

    def ids(self, *objects):
        return {str(obj.pk) for obj in objects}

    def test_default_search_is_substring(self):
        self.assertEqual(
            self.search_ids(self.url_events, "163.10.34.15", exact=False),
            self.ids(self.event_ip, self.event_ip_longer),
        )

    def test_exact_ip(self):
        self.assertEqual(
            self.search_ids(self.url_events, "163.10.34.15"),
            self.ids(self.event_ip),
        )

    def test_exact_cidr(self):
        self.assertEqual(
            self.search_ids(self.url_events, "163.10.34.0/24"),
            self.ids(self.event_network),
        )

    def test_exact_domain(self):
        self.assertEqual(
            self.search_ids(self.url_events, "UNLP.edu.ar"),
            self.ids(self.event_domain),
        )

    def test_exact_partial_ip_matches_nothing(self):
        self.assertEqual(self.search_ids(self.url_events, "163.10.34"), set())

    def test_exact_ip_in_cases(self):
        self.assertEqual(
            self.search_ids(self.url_cases, "163.10.34.15"),
            self.ids(self.case_ip),
        )

    def test_exact_text_matches_whole_words(self):
        taxonomy = Taxonomy.objects.get(slug="copyright")
        taxonomy.description = "Unauthorized use of copyrighted material"
        taxonomy.save()

        self.assertIn(
            str(taxonomy.pk), self.search_ids(self.url_taxonomies, "copyrighted")
        )
        self.assertNotIn(
            str(taxonomy.pk), self.search_ids(self.url_taxonomies, "copyrigh")
        )
        self.assertIn(
            str(taxonomy.pk),
            self.search_ids(self.url_taxonomies, "copyrigh", exact=False),
        )

    def test_exact_terms_are_combined_with_and(self):
        self.assertEqual(
            self.search_ids(self.url_events, "163.10.34.15 unlp.edu.ar"), set()
        )
        self.assertEqual(
            self.search_ids(self.url_events, "163.10.34.15 copyright"),
            self.ids(self.event_ip),
        )
