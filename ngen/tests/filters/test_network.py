"""
Django Network filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import NetworkFilter
from ngen.models import Contact, Network, NetworkEntity
from ngen.tests.filters.base_filter_test import BaseFilterTest


class NetworkFilterTest(BaseFilterTest):
    """
    Network filter test class.
    """

    fixtures = ["priority.json", "user.json", "network_entity.json", "contact.json"]

    @classmethod
    def setUpTestData(cls):
        cls.basename = "network"
        super().setUpTestData()

        cls.contact_1 = Contact.objects.get(pk=1)
        cls.entity_1 = NetworkEntity.objects.get(pk=1)

        cls.network_1 = Network.objects.create(
            domain="unlp.edu.ar",
            active=True,
            type="internal",
            network_entity=cls.entity_1
        )
        cls.network_1.created = timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        cls.network_1.save()
        cls.network_1.contacts.set([cls.contact_1])

        cls.network_2 = Network.objects.create(
            domain="info.unlp.edu.ar",
            active=True,
            type="external",
            parent=cls.network_1
        )
        cls.network_1.children.set([cls.network_2])

        cls.network_3 = Network.objects.create(
            cidr="10.0.0.0/24",
            active=False,
            type="internal"
        )

        cls.queryset = Network.objects.all()

        cls.filter = lambda query_params: NetworkFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        self.authenticate()

        # Searching by cidr
        query = "/24"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.network_3.id
        )

        # Searching by domain
        query = "info.unlp"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.network_2.id
        )

        # Searching by type
        query = "internal"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.network_1.id
        )
        self.assertEqual(
            self.get_id_from_url(response.data["results"][1]["url"]),
            self.network_3.id
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
            "id": self.network_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2000-01-01",
            "created_range_before": "2000-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_1])

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
            [self.network_1, self.network_2, self.network_3],
            ordered=False
        )

    def test_filter_by_cidr(self):
        """
        Test filter by cidr.
        """

        params = {
            "cidr": "10.0.0.0/24"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_3])

        params = {
            "is_subnet_of": "10.0.0.0/16"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_3])

    def test_filter_by_domain(self):
        """
        Test filter by domain.
        """

        params = {
            "domain": "unlp.edu.ar"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_1])

        params = {
            "is_subdomain_of": "unlp.edu.ar"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.network_1, self.network_2],
            ordered=False
        )

    def test_filter_by_active(self):
        """
        Test filter by active.
        """

        params = {
            "active": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.network_1, self.network_2],
            ordered=False
        )

    def test_filter_by_type(self):
        """
        Test filter by type.
        """

        params = {
            "type": "internal"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.network_1, self.network_3],
            ordered=False
        )

    def test_filter_by_network_entity(self):
        """
        Test filter by network_entity.
        """

        params = {
            "network_entity": self.entity_1
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_1])

    def test_filter_by_contacts(self):
        """
        Test filter by contacts.
        """

        params = {
            "contacts": [self.contact_1]
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_1])

    def test_filter_by_parent(self):
        """
        Test filter by parent.
        """

        params = {
            "parent": self.network_1
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_2])

        params = {
            "parent__isnull": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.network_1, self.network_3],
            ordered=False
        )

    def test_filter_by_children(self):
        """
        Test filter by children.
        """

        params = {
            "children": [self.network_2]
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.network_1])

        params = {
            "children__isnull": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.network_2, self.network_3],
            ordered=False
        )
