"""
Django Event filter tests. Tests search_fields and filterset_class.
"""
import pytz
from django.utils import timezone
from rest_framework.test import APITestCase
from django.urls import reverse
from ngen.filters import EventFilter

from ngen.models import Event, Tlp, Priority, Taxonomy, Feed, User, Case


class EventFilterTest(APITestCase):
    """
    Event filter test class.
    """

    fixtures = [
        "priority.json", "feed.json", "tlp.json", "user.json", "taxonomy.json", "state.json",
        "edge.json", "report.json", "network_entity.json", "network.json", "contact.json",
        "case_template.json",
    ]

    @classmethod
    def setUpTestData(cls):
        basename = "event"
        cls.url_list = reverse(f"{basename}-list")
        cls.url_login_jwt = reverse("token-create")
        cls.json_login = {"username": "ngen", "password": "ngen"}
        cls.search_url = lambda query: f"{cls.url_list}?search={query}"

        cls.feed_1 = Feed.objects.get(pk=1)
        cls.feed_2 = Feed.objects.get(pk=2)
        cls.feed_3 = Feed.objects.get(pk=3)
        cls.tlp_1 = Tlp.objects.get(pk=1)
        cls.tlp_2 = Tlp.objects.get(pk=2)
        cls.tlp_3 = Tlp.objects.get(pk=3)
        cls.priority_1 = Priority.objects.get(pk=1)
        cls.priority_2 = Priority.objects.get(pk=2)
        cls.priority_3 = Priority.objects.get(pk=3)
        cls.taxonomy_1 = Taxonomy.objects.get(pk=1)
        cls.taxonomy_2 = Taxonomy.objects.get(pk=2)
        cls.taxonomy_3 = Taxonomy.objects.get(pk=3)
        cls.user_1 = User.objects.get(username="ngen")
        cls.user_2 = User.objects.create(username="ngen2")

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
        cls.event_1.date = timezone.datetime(2024, 1, 1, tzinfo=pytz.UTC)
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
            cidr="10.0.0.0/24",
            taxonomy=cls.taxonomy_2,
            feed=cls.feed_1,
            tlp=cls.tlp_1,
            reporter=cls.user_2,
            notes="Some notes",
            priority=cls.priority_3,
            parent=cls.event_1
        )

        cls.queryset = Event.objects.all()

        cls.filter = lambda query_params: EventFilter(
            query_params,
            queryset=cls.queryset
        )

    def authenticate(self):
        """
        Authenticate user. Only needed for SearchFilter tests.
        """

        response = self.client.post(
            self.url_login_jwt, data=self.json_login, format="json")
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + response.data["access"])

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        self.authenticate()

        # Searching by taxonomy name
        query = "black"  # matches with taxonomy 1: "Blacklist"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            response.data["results"][0]["uuid"],
            str(self.event_1.uuid)
        )
        self.assertEqual(
            response.data["results"][1]["uuid"],
            str(self.event_4.uuid)
        )

        # Searching by feed name
        query = "bro"  # matches with feed 2: "Bro"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            response.data["results"][0]["uuid"],
            str(self.event_2.uuid)
        )
        self.assertEqual(
            response.data["results"][1]["uuid"],
            str(self.event_4.uuid)
        )

        # Searching by cidr
        query = "/16"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"],
            str(self.event_4.uuid)
        )

        # Searching by domain
        query = "info.unlp"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"],
            str(self.event_1.uuid)
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
            "created_after": "2024-01-01",
            "created_before": "2024-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_1, self.event_2, self.event_3, self.event_4, self.event_5],
            ordered=False
        )

    def test_filter_by_modified_range(self):
        """
        Test filter by modified range.
        """

        params = {
            "modified_after": "2024-01-01",
            "modified_before": "2024-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.event_1, self.event_2, self.event_3, self.event_4, self.event_5],
            ordered=False
        )

    def test_filter_by_date(self):
        """
        Test filter by date.
        """

        params = {
            "date": "2024-01-01"
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
            [self.event_1, self.event_4],
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
            [self.event_1, self.event_2, self.event_3, self.event_4],
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
            [self.event_2, self.event_3, self.event_4, self.event_5],
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
            [self.event_1, self.event_2, self.event_3, self.event_4],
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
            [self.event_4, self.event_5],
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
            [self.event_1, self.event_2],
            ordered=False
        )
