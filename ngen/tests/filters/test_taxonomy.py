"""
Django Taxonomy filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import TaxonomyFilter
from ngen.models import Taxonomy, Playbook
from ngen.tests.filters.base_filter_test import BaseFilterTest


class TaxonomyFilterTest(BaseFilterTest):
    """
    Taxonomy filter test class.
    """

    fixtures = ['priority.json', 'user.json']

    @classmethod
    def setUpTestData(cls):
        cls.basename = "taxonomy"
        super().setUpTestData()

        cls.playbook_1 = Playbook.objects.create(
            name="Botnet Playbook"
        )

        cls.taxonomy_1 = Taxonomy.objects.create(
            name="Botnet",
            slug="botnet",
            type="vulnerability",
            active=True,
            description="First taxonomy"
        )
        cls.taxonomy_1.created = timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        cls.taxonomy_1.save()
        cls.taxonomy_1.playbooks.set([cls.playbook_1])
        cls.playbook_1.taxonomy.set([cls.taxonomy_1])

        cls.taxonomy_2 = Taxonomy.objects.create(
            name="Information Leakage",
            slug="information_leakage",
            type="vulnerability",
            active=True,
            description="Second taxonomy",
            parent=cls.taxonomy_1
        )

        cls.taxonomy_3 = Taxonomy.objects.create(
            name="Mail Leak",
            slug="mail_leak",
            type="incident",
            active=False,
            description="Third taxonomy",
            parent=cls.taxonomy_1
        )

        cls.queryset = Taxonomy.objects.all()

        cls.filter = lambda query_params: TaxonomyFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        # Searching by name
        query = "bot"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.taxonomy_1.id
        )

        # Searching by description
        query = "second"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.taxonomy_2.id
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
            "id": self.taxonomy_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.taxonomy_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2000-01-01",
            "created_range_before": "2000-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.taxonomy_1])

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
            [self.taxonomy_1, self.taxonomy_2, self.taxonomy_3],
            ordered=False
        )

    def test_filter_by_name(self):
        """
        Test filter by name.
        """

        params = {
            "name__icontains": "leak"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.taxonomy_2, self.taxonomy_3])

    def test_filter_by_slug(self):
        """
        Test filter by slug.
        """

        params = {
            "slug__icontains": "leak"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.taxonomy_2, self.taxonomy_3])

    def test_filter_by_description(self):
        """
        Test filter by description.
        """

        params = {
            "description__icontains": "second"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.taxonomy_2])

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
            [self.taxonomy_1, self.taxonomy_2],
            ordered=False
        )

    def test_filter_by_type(self):
        """
        Test filter by type.
        """

        params = {
            "type": "vulnerability"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.taxonomy_1, self.taxonomy_2],
            ordered=False
        )

    def test_filter_by_playbooks(self):
        """
        Test filter by playbooks.
        """

        params = {
            "playbooks": [self.playbook_1]
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.taxonomy_1])

    def test_filter_by_parent(self):
        """
        Test filter by parent.
        """

        params = {
            "parent": self.taxonomy_1
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.taxonomy_2, self.taxonomy_3])

        params = {
            "parent__isnull": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.taxonomy_1],
            ordered=False
        )

    def test_filter_by_children(self):
        """
        Test filter by children.
        """

        params = {
            "children": [self.taxonomy_2]
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.taxonomy_1])

        params = {
            "children__isnull": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset,
            [self.taxonomy_2, self.taxonomy_3],
            ordered=False
        )
