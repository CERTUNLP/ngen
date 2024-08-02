"""
Django Event filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import EventFilter
from ngen.models import Event, Tlp, Priority, Taxonomy, Feed, User, Case
from ngen.tests.filters.base_filter_test import BaseFilterTest


class EventFilterTest(BaseFilterTest):
    """
    Event filter test class.
    """

    fixtures = [
        "priority.json", "feed.json", "tlp.json", "user.json", "taxonomy_group.json", "taxonomy.json", "state.json",
        "case_template.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.basename = "event"
        super().setUpTestData()

        cls.feed_1 = Feed.objects.get(slug="csirtamericas")
        cls.feed_2 = Feed.objects.get(slug="bro")
        cls.feed_3 = Feed.objects.get(slug="censys")
        cls.tlp_1 = Tlp.objects.get(slug="white")
        cls.tlp_2 = Tlp.objects.get(slug="green")
        cls.tlp_3 = Tlp.objects.get(slug="amber")
        cls.priority_1 = Priority.objects.get(slug="critical")
        cls.priority_2 = Priority.objects.get(slug="high")
        cls.priority_3 = Priority.objects.get(slug="medium")
        cls.taxonomy_1 = Taxonomy.objects.get_by_slug(slug="blacklist")
        cls.taxonomy_2 = Taxonomy.objects.get_by_slug(slug="botnet")
        cls.taxonomy_3 = Taxonomy.objects.get_by_slug(slug="botnet_attack_command")
        cls.user_1 = User.objects.get(username="ngen")
        cls.user_2 = User.objects.create(username="ngen2", password="ngen2")

        cls.event_1 = Event.objects.create(  # matches with case template
            uuid="00000000-0000-0000-0000-000000000001",
            domain="info.unlp.edu.ar",
            taxonomy=cls.taxonomy_1,
            feed=cls.feed_1,
            tlp=cls.tlp_1,
            reporter=cls.user_1,
            notes="Some notes",
            priority=cls.priority_1,
        )
        # bypass date auto_now_add
        cls.event_1.date = timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        cls.event_1.created = timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        cls.event_1.save()

        cls.event_2 = Event.objects.create(
            uuid="00000000-0000-0000-0000-000000000002",
            domain="unlp.edu.ar",
            taxonomy=cls.taxonomy_2,
            feed=cls.feed_2,
            tlp=cls.tlp_2,
            reporter=cls.user_1,
            notes="Some notes",
            priority=cls.priority_2,
        )

        cls.event_3 = Event.objects.create(
            uuid="00000000-0000-0000-0000-000000000003",
            domain="cert.edu.ar",
            taxonomy=cls.taxonomy_3,
            feed=cls.feed_3,
            tlp=cls.tlp_3,
            reporter=cls.user_1,
            notes="Some notes",
            priority=cls.priority_3,
        )

        cls.event_4 = Event.objects.create(
            uuid="00000000-0000-0000-0000-000000000004",
            cidr="10.0.0.0/16",
            taxonomy=cls.taxonomy_1,
            feed=cls.feed_2,
            tlp=cls.tlp_3,
            reporter=cls.user_1,
            notes="Some notes",
            priority=cls.priority_3,
        )

        cls.event_5 = Event.objects.create(
            uuid="00000000-0000-0000-0000-000000000005",
            domain="info.unlp.edu.ar",
            taxonomy=cls.taxonomy_1,
            feed=cls.feed_1,
            tlp=cls.tlp_1,
            reporter=cls.user_1,
            notes="Some notes",
            priority=cls.priority_1,
        )

        cls.event_6 = Event.objects.create(
            uuid="00000000-0000-0000-0000-000000000006",
            cidr="10.0.0.0/24",
            taxonomy=cls.taxonomy_2,
            feed=cls.feed_1,
            tlp=cls.tlp_1,
            reporter=cls.user_2,
            notes="Some notes",
            priority=cls.priority_3,
        )

        cls.queryset = Event.objects.all()

        cls.filter = lambda query_params: EventFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        # Searching by taxonomy name
        query = "black"  # matches with taxonomy 1: "Blacklist"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.event_1.id
        )
        self.assertEqual(
            self.get_id_from_url(response.data["results"][1]["url"]),
            self.event_4.id
        )

        # Searching by feed name
        query = "bro"  # matches with feed 2: "Bro"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.event_2.id
        )
        self.assertEqual(
            self.get_id_from_url(response.data["results"][1]["url"]),
            self.event_4.id
        )

        # Searching by cidr
        query = "/16"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.event_4.id
        )

        # Searching by domain
        query = "info.unlp"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.event_1.id
        )

        # Searching with no results
        query = "no results"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 0)

    def test_filter_by_id(self):
        """
        Test filter by id.
        """

        params = {
            "id": self.event_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.event_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2000-01-01",
            "created_range_before": "2000-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.event_1])

    def test_filter_by_modified_range(self):
        """
        Test filter by modified range.
        """

        today = today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)

        params = {
            "modified_range_after": today.isoformat(),
            "modified_range_before": tomorrow.isoformat()
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_1, self.event_2, self.event_3, self.event_4, self.event_5, self.event_6],
            ordered=False
        )

    def test_filter_by_date(self):
        """
        Test filter by date.
        """

        params = {
            "date": "2000-01-01"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.event_1])

    def test_filter_by_feed(self):
        """
        Test filter by feed.
        """

        params = {
            "feed": self.feed_2
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_2, self.event_4],
            ordered=False
        )

    def test_filter_by_tlp(self):
        """
        Test filter by tlp.
        """

        params = {
            "tlp": self.tlp_3
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_3, self.event_4],
            ordered=False
        )

    def test_filter_by_priority(self):
        """
        Test filter by priority.
        """

        params = {
            "priority": self.priority_2
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.event_2])

    def test_filter_by_taxonomy(self):
        """
        Test filter by taxonomy.
        """

        params = {
            "taxonomy": self.taxonomy_1
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_1, self.event_4, self.event_5],
            ordered=False
        )

    def test_filter_by_parent(self):
        """
        Test filter by parent.
        """

        params = {
            "parent": self.event_1
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.event_5])

        params = {
            "parent__isnull": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_1, self.event_2, self.event_3, self.event_4, self.event_6],
            ordered=False
        )

    def test_filter_by_case(self):
        """
        Test filter by case.
        """

        params = {
            "case": Case.objects.first()
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.event_1])

        params = {
            "case__isnull": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_2, self.event_3, self.event_4, self.event_5, self.event_6],
            ordered=False
        )

    def test_filter_by_reporter(self):
        """
        Test filter by reporter.
        """

        params = {
            "reporter": self.user_1
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_1, self.event_2, self.event_3, self.event_4, self.event_5],
            ordered=False
        )

    def test_filter_by_uuid(self):
        """
        Test filter by uuid.
        """

        params = {
            "uuid": "00000000-0000-0000-0000-000000000002"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.event_2])

    def test_filter_by_cidr(self):
        """
        Test filter by cidr.
        """

        params = {
            "cidr": "10.0.0.0/16"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.event_4])

        params = {
            "is_subnet_of": "10.0.0.0/16"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_4, self.event_6],
            ordered=False
        )

    def test_filter_by_domain(self):
        """
        Test filter by domain.
        """

        params = {
            "domain": "cert.edu.ar"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.event_3])

        params = {
            "is_subdomain_of": "unlp.edu.ar"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_1, self.event_2, self.event_5],
            ordered=False
        )
