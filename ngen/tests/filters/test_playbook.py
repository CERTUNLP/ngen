"""
Django Playbook filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import PlaybookFilter
from ngen.models import Playbook, Taxonomy
from ngen.tests.filters.base_filter_test import BaseFilterTest


class PlaybookFilterTest(BaseFilterTest):
    """
    Playbook filter test class.
    """

    fixtures = ['priority.json', 'user.json', 'taxonomy.json']

    @classmethod
    def setUpTestData(cls):
        cls.basename = "playbook"
        super().setUpTestData()

        cls.taxonomy_1 = Taxonomy.objects.get(pk=90)
        cls.taxonomy_2 = Taxonomy.objects.get(pk=41)

        cls.playbook_1 = Playbook.objects.create(
            name="Phish playbook"
        )
        cls.playbook_1.created = timezone.datetime(2024, 1, 1, tzinfo=pytz.UTC)
        cls.playbook_1.save()
        cls.playbook_1.taxonomy.set([cls.taxonomy_1])

        cls.playbook_2 = Playbook.objects.create(
            name="Copyright playbook",
        )
        cls.playbook_2.taxonomy.set([cls.taxonomy_2])

        cls.queryset = Playbook.objects.all()

        cls.filter = lambda query_params: PlaybookFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        self.authenticate()

        # Searching by name
        query = "phish"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.playbook_1.id
        )

        # Searching by taxonomy name
        query = "ing"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.playbook_1.id
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
            "id": self.playbook_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.playbook_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2024-01-01",
            "created_range_before": "2024-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.playbook_1])

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
            [self.playbook_1, self.playbook_2],
            ordered=False
        )

    def test_filter_by_name(self):
        """
        Test filter by name.
        """

        params = {
            "name__icontains": "phish"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.playbook_1])

    def test_filter_by_taxonomy(self):
        """
        Test filter by taxonomy.
        """

        params = {
            "taxonomy": [self.taxonomy_1]
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.playbook_1])
