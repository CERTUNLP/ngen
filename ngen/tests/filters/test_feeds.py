"""
Django Feed filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import FeedFilter
from ngen.models import Feed
from ngen.tests.filters.base_filter_test import BaseFilterTest


class FeedFilterTest(BaseFilterTest):
    """
    Feed filter test class.
    """

    fixtures = ['user.json', 'priority.json']

    @classmethod
    def setUpTestData(cls):
        cls.basename = "feed"
        super().setUpTestData()

        cls.feed_1 = Feed.objects.create(
            name="ABC",
            description="Feed ABC description 123"
        )
        cls.feed_1.created = timezone.datetime(2024, 1, 1, tzinfo=pytz.UTC)
        cls.feed_1.save()

        cls.feed_2 = Feed.objects.create(
            name="BCD",
            description="Feed BCD description 456"
        )

        cls.feed_3 = Feed.objects.create(
            name="CDE-1",
            description="Feed CDE description 789",
            active=False
        )

        cls.queryset = Feed.objects.all()

        cls.filter = lambda query_params: FeedFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        self.authenticate()

        # Searching by name
        query = "bc"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 2)

        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.feed_1.id
        )
        self.assertEqual(
            self.get_id_from_url(response.data["results"][1]["url"]),
            self.feed_2.id
        )

        # Searching by description
        query = "789"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.feed_3.id
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
            "id": self.feed_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.feed_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2024-01-01",
            "created_range_before": "2024-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.feed_1])

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
            [self.feed_1, self.feed_2, self.feed_3],
            ordered=False
        )

    def test_filter_by_name(self):
        """
        Test filter by name.
        """

        params = {
            "name__icontains": "bc"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.feed_1, self.feed_2], ordered=False)

        params = {
            "name__icontains": "ABC"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.feed_1])

    def test_filter_by_slug(self):
        """
        Test filter by slug.
        """

        params = {
            "slug__icontains": "bc"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.feed_1, self.feed_2], ordered=False)

        params = {
            "slug__icontains": "cde_1"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.feed_3])

    def test_filter_by_description(self):
        """
        Test filter by description.
        """

        params = {
            "description__icontains": "456"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.feed_2])

        params = {
            "description__icontains": "description"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.feed_1, self.feed_2, self.feed_3], ordered=False)

    def test_filter_by_active(self):
        """
        Test filter by active.
        """

        params = {
            "active": False
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.feed_3])
