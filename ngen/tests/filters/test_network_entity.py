"""
Django Network Entity filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import NetworkEntityFilter
from ngen.models import NetworkEntity, Network
from ngen.tests.filters.base_filter_test import BaseFilterTest


class NetworkEntityFilterTest(BaseFilterTest):
    """
    Network Entity filter test class.
    """

    fixtures = ["user.json", "priority.json"]

    @classmethod
    def setUpTestData(cls):
        cls.basename = "networkentity"
        super().setUpTestData()

        cls.network_entity_1 = NetworkEntity.objects.create(
            name="Universidad Nacional de La Plata",
            slug="universidad_nacional_de_la_plata",
            active=True,
        )
        cls.network_entity_1.created = timezone.datetime(2024, 1, 1, tzinfo=pytz.UTC)
        cls.network_entity_1.save()

        cls.network_entity_2 = NetworkEntity.objects.create(
            name="Universidad de Buenos Aires",
            slug="universidad_de_buenos_aires",
            active=True,
        )

        cls.network_entity_3 = NetworkEntity.objects.create(
            name="Universidad Nacional de Córdoba",
            slug="universidad_nacional_de_cordoba",
            active=False,
        )

        cls.network_1 = Network.objects.create(
            domain="unlp.edu.ar",
            active=True,
            type="internal",
            network_entity=cls.network_entity_1,
        )

        cls.queryset = NetworkEntity.objects.all()

        cls.filter = lambda query_params: NetworkEntityFilter(
            query_params, queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        self.authenticate()

        # Searching by name
        query = "plata"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.network_entity_1.id,
        )

        # Searching by slug
        query = "buenos_aires"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.network_entity_2.id,
        )

        # Searching with no results
        query = "no results"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 0)

    def test_filter_by_id(self):
        """
        Test filter by id.
        """

        params = {"id": self.network_entity_1.id}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_entity_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2024-01-01",
            "created_range_before": "2024-01-02",
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_entity_1])

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
            [self.network_entity_1, self.network_entity_2, self.network_entity_3],
            ordered=False,
        )

    def test_filter_by_name(self):
        """
        Test filter by name.
        """

        params = {"name__icontains": "buenos"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_entity_2])

    def test_filter_by_slug(self):
        """
        Test filter by slug.
        """

        params = {"slug__icontains": "plata"}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_entity_1])

    def test_filter_by_active(self):
        """
        Test filter by active.
        """

        params = {"active": False}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_entity_3])

    def test_filter_by_network(self):
        """
        Test filter by network.
        """

        params = {"networks": [self.network_1]}

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_entity_1])
