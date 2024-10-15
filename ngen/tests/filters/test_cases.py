"""
Django Case filter tests. Tests search_fields and filterset_class.
"""

import datetime

import pytz
from django.utils import timezone

from ngen.filters import CaseFilter
from ngen.models import (
    Tlp,
    Priority,
    Taxonomy,
    Feed,
    User,
    Case,
    CaseTemplate,
    State,
    Event,
)
from ngen.tests.filters.base_filter_test import BaseFilterTest


class CaseFilterTest(BaseFilterTest):
    """
    Case filter test class.
    """

    fixtures = [
        "tests/priority.json",
        "tests/feed.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/taxonomy.json",
        "tests/state.json",
        "tests/case_template.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.basename = "case"
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
        cls.user_1 = User.objects.get(username="ngen")
        cls.case_template_1 = CaseTemplate.objects.get(pk=1)
        cls.case_template_2 = CaseTemplate.objects.get(pk=2)
        cls.event_1 = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=cls.taxonomy_3,
            feed=cls.feed_3,
            tlp=cls.tlp_3,
            reporter=cls.user_1,
            notes="Some notes",
            priority=cls.priority_1,
        )
        cls.event_2 = Event.objects.create(
            cidr="10.0.1.0/24",
            taxonomy=cls.taxonomy_3,
            feed=cls.feed_3,
            tlp=cls.tlp_3,
            reporter=cls.user_1,
            notes="Some notes",
            priority=cls.priority_2,
        )

        cls.case_1 = Case.objects.create(
            uuid="00000000-0000-0000-0000-000000000001",
            priority=cls.priority_1,
            tlp=cls.tlp_1,
            casetemplate_creator=cls.case_template_1,
            state=cls.state_2,
            lifecycle="manual",
        )
        cls.case_1.date = timezone.datetime(
            2000, 1, 1, tzinfo=pytz.UTC
        )  # bypass date auto_now_add
        cls.case_1.created = timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        cls.case_1.attend_date = timezone.datetime(2000, 1, 2, tzinfo=pytz.UTC)
        cls.case_1.solve_date = timezone.datetime(2000, 1, 3, tzinfo=pytz.UTC)
        cls.case_1.save()

        cls.case_2 = Case.objects.create(
            uuid="00000000-0000-0000-0000-000000000002",
            priority=cls.priority_2,
            tlp=cls.tlp_2,
            casetemplate_creator=cls.case_template_1,
            state=cls.state_1,
            lifecycle="manual",
            assigned=cls.user_1,
        )
        cls.case_2.events.set([cls.event_1])

        cls.case_3 = Case.objects.create(
            uuid="00000000-0000-0000-0000-000000000003",
            priority=cls.priority_3,
            tlp=cls.tlp_3,
            casetemplate_creator=cls.case_template_1,
            state=cls.state_1,
            lifecycle="auto",
        )
        cls.case_3.events.set([cls.event_2])

        cls.case_4 = Case.objects.create(
            uuid="00000000-0000-0000-0000-000000000004",
            priority=cls.priority_1,
            tlp=cls.tlp_2,
            casetemplate_creator=cls.case_template_1,
            state=cls.state_1,
            lifecycle="auto",
        )

        cls.case_5 = Case.objects.create(
            uuid="00000000-0000-0000-0000-000000000005",
            priority=cls.priority_2,
            tlp=cls.tlp_3,
            casetemplate_creator=cls.case_template_2,
            state=cls.state_1,
            lifecycle="auto",
            parent=cls.case_1,
        )

        cls.queryset = Case.objects.all()

        cls.filter = lambda query_params: CaseFilter(
            query_params, queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        # Searching by cidr
        query = "10.0.1.0"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]), self.case_3.id
        )

        # Searching by domain
        query = "unlp.edu.ar"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]), self.case_2.id
        )

        # Searching with no results
        query = "no results"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 0)

    def test_filter_by_id(self):
        """
        Test filter by id.
        """

        params = {"id": self.case_1.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2000-01-01",
            "created_range_before": "2000-01-02",
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_1])

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
            [self.case_1, self.case_2, self.case_3, self.case_4, self.case_5],
            ordered=False,
        )

    def test_filter_by_date(self):
        """
        Test filter by date.
        """

        params = {"date": "2000-01-01"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_1])

    def test_filter_by_attend_date(self):
        """
        Test filter by attend_date.
        """

        params = {"attend_date": "2000-01-02"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_1])

    def test_filter_by_solve_date(self):
        """
        Test filter by solve_date.
        """

        params = {"solve_date": "2000-01-03"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_1])

    def test_filter_by_lifecycle(self):
        """
        Test filter by lifecycle.
        """

        params = {"lifecycle": "manual"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_1, self.case_2])

    def test_filter_by_priority(self):
        """
        Test filter by priority.
        """

        params = {"priority": self.priority_1.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_1, self.case_4])

    def test_filter_by_tlp(self):
        """
        Test filter by tlp.
        """

        params = {"tlp": self.tlp_1.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_1])

    def test_filter_by_casetemplate_creator(self):
        """
        Test filter by casetemplate_creator.
        """

        params = {"casetemplate_creator": self.case_template_1.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.case_1, self.case_2, self.case_3, self.case_4],
            ordered=False,
        )

    def test_filter_by_uuid(self):
        """
        Test filter by uuid.
        """

        params = {"uuid": "00000000-0000-0000-0000-000000000002"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_2])

    def test_filter_by_parent(self):
        """
        Test filter by parent.
        """

        params = {"parent": self.case_1}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_5])

        params = {"parent__isnull": True}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.case_1, self.case_2, self.case_3, self.case_4],
            ordered=False,
        )

    def test_filter_by_assigned(self):
        """
        Test filter by assigned.
        """

        params = {"assigned": self.user_1}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_2])

        params = {"assigned__isnull": True}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.case_1, self.case_3, self.case_4, self.case_5],
            ordered=False,
        )

    def test_filter_by_state(self):
        """
        Test filter by state.
        """

        params = {"state": self.state_2.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_1])

    def test_filter_by_event_cidr(self):
        """
        Test filter by event cidr.
        """

        params = {"event_cidr": "10.0.0.0/16"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_3])

        params = {"event_cidr": "10.0.1.0/24"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_3])

    def test_filter_by_event_domain(self):
        """
        Test filter by event domain.
        """

        params = {"event_domain": "info.unlp.edu.ar"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_2])

        params = {"event_domain": "unlp.edu.ar"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.case_2])
