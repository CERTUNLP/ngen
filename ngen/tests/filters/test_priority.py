"""
Django Priority filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import PriorityFilter
from ngen.models import Priority
from ngen.tests.filters.base_filter_test import BaseFilterTest


class PriorityFilterTest(BaseFilterTest):
    """
    Priority filter test class.
    """

    fixtures = ['priority.json', 'user.json']

    @classmethod
    def setUpTestData(cls):
        cls.basename = "priority"
        super().setUpTestData()

        cls.priority_1 = Priority.objects.create(
            name="Priority One",
            slug="priority_one",
            severity=700,
            attend_time=datetime.timedelta(minutes=30),
            solve_time=datetime.timedelta(minutes=10),
            notification_amount=100
        )
        cls.priority_1.created = timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        cls.priority_1.save()

        cls.priority_2 = Priority.objects.create(
            name="Priority Two",
            slug="priority_two",
            severity=800,
            attend_time=datetime.timedelta(minutes=30),
            solve_time=datetime.timedelta(minutes=10),
            notification_amount=200
        )

        cls.priority_3 = Priority.objects.create(
            name="Priority Three",
            slug="priority_three",
            severity=900,
            attend_time=datetime.timedelta(minutes=10),
            solve_time=datetime.timedelta(minutes=30),
            notification_amount=200
        )

        cls.queryset = Priority.objects.all()

        cls.filter = lambda query_params: PriorityFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        # Searching by name
        query = "two"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.priority_2.id
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
            "id": self.priority_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.priority_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2000-01-01",
            "created_range_before": "2000-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.priority_1])

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
        expected_values = set(
            [self.priority_1, self.priority_2, self.priority_3]
        )

        self.assertTrue(expected_values.issubset(filtered_queryset))

    def test_filter_by_name(self):
        """
        Test filter by name.
        """

        params = {
            "name__icontains": "two"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.priority_2])

        params = {
            "name__icontains": "priority"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.priority_1, self.priority_2, self.priority_3],
            ordered=False
        )

    def test_filter_by_slug(self):
        """
        Test filter by slug.
        """

        params = {
            "slug__icontains": "two"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.priority_2])

        params = {
            "slug__icontains": "priority"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.priority_1, self.priority_2, self.priority_3],
            ordered=False
        )

    def test_filter_by_severity(self):
        """
        Test filter by severity.
        """

        params = {
            "severity": 700
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.priority_1])

    def test_filter_by_attend_time(self):
        """
        Test filter by attend_time.
        """

        params = {
            "attend_time": datetime.timedelta(minutes=30)
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.priority_1, self.priority_2])

    def test_filter_by_solve_time(self):
        """
        Test filter by solve_time.
        """

        params = {
            "solve_time": datetime.timedelta(minutes=30)
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.priority_3])

    def test_filter_by_notification_amount(self):
        """
        Test filter by notification_amount.
        """

        params = {
            "notification_amount": 200
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.priority_2, self.priority_3])
