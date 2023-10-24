"""
Django State filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import StateFilter
from ngen.models import State
from ngen.tests.filters.base_filter_test import BaseFilterTest


class StateFilterTest(BaseFilterTest):
    """
    State filter test class.
    """

    fixtures = ["user.json", "priority.json"]

    @classmethod
    def setUpTestData(cls):
        cls.basename = "state"
        super().setUpTestData()

        cls.state_1 = State.objects.create(
            slug="initial",
            name="Initial",
            blocked=False,
            attended=False,
            solved=False,
            active=True,
            description="Initial state"
        )
        cls.state_1.created = timezone.datetime(2024, 1, 1, tzinfo=pytz.UTC)
        cls.state_1.save()

        cls.state_2 = State.objects.create(
            slug="open",
            name="Open",
            blocked=False,
            attended=True,
            solved=False,
            active=True,
            description="Open state"
        )

        cls.state_3 = State.objects.create(
            slug="closed",
            name="Closed",
            blocked=True,
            attended=False,
            solved=True,
            active=False,
            description="Closed state"
        )

        cls.state_1.children.set([cls.state_3])

        cls.queryset = State.objects.all()

        cls.filter = lambda query_params: StateFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        self.authenticate()

        # Searching by name
        query = "init"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.state_1.id
        )

        # Searching by description
        query = "open state"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.state_2.id
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
            "id": self.state_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.state_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2024-01-01",
            "created_range_before": "2024-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.state_1])

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
            [self.state_1, self.state_2, self.state_3],
            ordered=False
        )

    def test_filter_by_slug(self):
        """
        Test filter by slug.
        """

        params = {
            "slug__icontains": "open"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.state_2])

    def test_filter_by_name(self):
        """
        Test filter by name.
        """

        params = {
            "name__icontains": "closed"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.state_3])

    def test_filter_by_blocked(self):
        """
        Test filter by blocked.
        """

        params = {
            "blocked": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.state_3])

    def test_filter_by_attended(self):
        """
        Test filter by attended.
        """

        params = {
            "attended": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.state_2])

    def test_filter_by_solved(self):
        """
        Test filter by solved.
        """

        params = {
            "solved": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.state_3])

    def test_filter_by_active(self):
        """
        Test filter by active.
        """

        params = {
            "active": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.state_1, self.state_2], ordered=False)

    def test_filter_by_description(self):
        """
        Test filter by description.
        """

        params = {
            "description__icontains": "open"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.state_2])

    def test_filter_by_children(self):
        """
        Test filter by children.
        """

        params = {
            "children": [self.state_3]
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.state_1])

        params = {
            "children__isnull": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.state_2, self.state_3], ordered=False)
