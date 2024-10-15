"""
Django Case Template filter tests. Tests search_fields and filterset_class.
"""

import datetime

import pytz
from django.utils import timezone

from ngen.filters import CaseTemplateFilter
from ngen.models import Tlp, Priority, Taxonomy, Feed, State, CaseTemplate
from ngen.tests.filters.base_filter_test import BaseFilterTest


class CaseTemplateFilterTest(BaseFilterTest):
    """
    Case Template filter test class.
    """

    fixtures = [
        "tests/priority.json",
        "tests/feed.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/taxonomy.json",
        "tests/state.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.basename = "casetemplate"
        super().setUpTestData()

        cls.feed_1 = Feed.objects.get(slug="csirtamericas")
        cls.feed_2 = Feed.objects.get(slug="bro")
        cls.feed_3 = Feed.objects.get(slug="censys")
        cls.tlp_1 = Tlp.objects.get(slug="clear")
        cls.tlp_2 = Tlp.objects.get(slug="green")
        cls.tlp_3 = Tlp.objects.get(slug="amber")
        cls.priority_1 = Priority.objects.get(slug="critical")
        cls.priority_2 = Priority.objects.get(slug="high")
        cls.priority_3 = Priority.objects.get(slug="medium")
        cls.taxonomy_1 = Taxonomy.objects.get(slug="blacklist")
        cls.taxonomy_2 = Taxonomy.objects.get(slug="botnet")
        cls.taxonomy_3 = Taxonomy.objects.get(slug="botnet_attack_command")
        cls.state_1 = State.objects.get(slug="open")
        cls.state_2 = State.objects.get(slug="staging")

        cls.casetemplate_1 = CaseTemplate.objects.create(
            domain="info.unlp.edu.ar",
            event_taxonomy=cls.taxonomy_1,
            event_feed=cls.feed_1,
            case_tlp=cls.tlp_1,
            case_state=cls.state_1,
            priority=cls.priority_1,
            case_lifecycle="auto",
            active=False,
        )
        CaseTemplate.objects.filter(id=cls.casetemplate_1.id).update(
            created=timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        )

        cls.casetemplate_2 = CaseTemplate.objects.create(
            domain="unlp.edu.ar",
            address_value="unlp.edu.ar",
            event_taxonomy=cls.taxonomy_2,
            event_feed=cls.feed_2,
            case_tlp=cls.tlp_2,
            case_state=cls.state_2,
            priority=cls.priority_2,
            case_lifecycle="auto",
            active=True,
        )

        cls.casetemplate_3 = CaseTemplate.objects.create(
            cidr="10.0.0.0/16",
            event_taxonomy=cls.taxonomy_3,
            event_feed=cls.feed_3,
            case_tlp=cls.tlp_3,
            case_state=cls.state_2,
            priority=cls.priority_3,
            case_lifecycle="manual",
            active=True,
        )

        cls.casetemplate_4 = CaseTemplate.objects.create(
            cidr="10.0.0.0/24",
            event_taxonomy=cls.taxonomy_3,
            event_feed=cls.feed_3,
            case_tlp=cls.tlp_3,
            case_state=cls.state_2,
            priority=cls.priority_3,
            case_lifecycle="manual",
            active=False,
        )

        cls.queryset = CaseTemplate.objects.all()

        cls.filter = lambda query_params: CaseTemplateFilter(
            query_params, queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        # Searching by cidr
        query = "/16"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.casetemplate_3.id,
        )

        # Searching by domain
        query = "unlp.edu.ar"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.casetemplate_1.id,
        )
        self.assertEqual(
            self.get_id_from_url(response.data["results"][1]["url"]),
            self.casetemplate_2.id,
        )

        # Searching with no results
        query = "no results"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 0)

    def test_filter_by_id(self):
        """
        Test filter by id.
        """

        params = {"id": self.casetemplate_1.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.casetemplate_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2000-01-01",
            "created_range_before": "2000-01-02",
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.casetemplate_1])

    def test_filter_by_modified_range(self):
        """
        Test filter by modified range.
        """

        today = today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)

        params = {
            "modified_range_after": today.isoformat(),
            "modified_range_before": tomorrow.isoformat(),
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [
                self.casetemplate_1,
                self.casetemplate_2,
                self.casetemplate_3,
                self.casetemplate_4,
            ],
            ordered=False,
        )

    def test_filter_by_event_taxonomy(self):
        """
        Test filter by event_taxonomy.
        """

        params = {"event_taxonomy": self.taxonomy_1}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.casetemplate_1])

    def test_filter_by_event_feed(self):
        """
        Test filter by event_feed.
        """

        params = {"event_feed": self.feed_2}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.casetemplate_2])

    def test_filter_by_case_tlp(self):
        """
        Test filter by case_tlp.
        """

        params = {"case_tlp": self.tlp_3}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.casetemplate_3, self.casetemplate_4], ordered=False
        )

    def test_filter_by_case_state(self):
        """
        Test filter by case_state.
        """

        params = {"case_state": self.state_1}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.casetemplate_1])

    def test_filter_by_priority(self):
        """
        Test filter by priority.
        """

        params = {"priority": self.priority_2}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.casetemplate_2])

    def test_filter_by_case_lifecycle(self):
        """
        Test filter by case_lifecycle.
        """

        params = {"case_lifecycle": "auto"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.casetemplate_1, self.casetemplate_2], ordered=False
        )

    def test_filter_by_active(self):
        """
        Test filter by active.
        """

        params = {"active": True}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.casetemplate_2, self.casetemplate_3], ordered=False
        )

    def test_filter_by_cidr(self):
        """
        Test filter by cidr.
        """

        params = {"cidr": "10.0.0.0/16"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.casetemplate_3])

        params = {"is_subnet_of": "10.0.0.0/16"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.casetemplate_3, self.casetemplate_4], ordered=False
        )

    def test_filter_by_domain(self):
        """
        Test filter by domain.
        """

        params = {"domain": "unlp.edu.ar"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.casetemplate_2])

        params = {"is_subdomain_of": "unlp.edu.ar"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.casetemplate_1, self.casetemplate_2], ordered=False
        )

    def test_filter_by_address_value(self):
        """
        Test filter by address_value.
        """

        params = {"address_value__icontains": "unlp.edu.ar"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.casetemplate_2])
