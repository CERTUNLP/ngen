"""
Django Contact filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import ContactFilter
from ngen.models import Priority, Contact
from ngen.tests.filters.base_filter_test import BaseFilterTest


class ContactFilterTest(BaseFilterTest):
    """
    Contact filter test class.
    """

    fixtures = ['user.json', 'priority.json']

    @classmethod
    def setUpTestData(cls):
        cls.basename = "contact"
        super().setUpTestData()

        cls.priority_1 = Priority.objects.get(pk=1)
        cls.priority_2 = Priority.objects.get(pk=2)
        cls.priority_3 = Priority.objects.get(pk=3)

        cls.contact_1 = Contact.objects.create(
            name="Soporte CERT",
            username="soporte@cert.unlp.edu.ar",
            type="email",
            role="administrative",
            priority=cls.priority_1
        )
        cls.contact_1.created = timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        cls.contact_1.save()

        cls.contact_2 = Contact.objects.create(
            name="Soporte Abusos",
            username="+5492211234567",
            type="phone",
            role="abuse",
            priority=cls.priority_2
        )

        cls.contact_3 = Contact.objects.create(
            name="Soporte Técnico",
            username="soporte_tecnico",
            type="telegram",
            role="technical",
            priority=cls.priority_3
        )

        cls.queryset = Contact.objects.all()

        cls.filter = lambda query_params: ContactFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        self.authenticate()

        # Searching by name
        query = "cert"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.contact_1.id
        )

        # Searching by username
        query = "221"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.contact_2.id
        )

        # Searching by role
        query = "admin"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.contact_1.id
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
            "id": self.contact_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.contact_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2000-01-01",
            "created_range_before": "2000-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.contact_1])

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
            [self.contact_1, self.contact_2, self.contact_3],
            ordered=False
        )

    def test_filter_by_name(self):
        """
        Test filter by name.
        """

        params = {
            "name__icontains": "cert"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.contact_1])

    def test_filter_by_username(self):
        """
        Test filter by username.
        """

        params = {
            "username__icontains": "cert"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.contact_1])

    def test_filter_by_type(self):
        """
        Test filter by type.
        """

        params = {
            "type": "phone"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.contact_2])

    def test_filter_by_role(self):
        """
        Test filter by role.
        """

        params = {
            "role": "technical"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.contact_3])

    def test_filter_by_priority(self):
        """
        Test filter by priority.
        """

        params = {
            "priority": self.priority_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.contact_1])
