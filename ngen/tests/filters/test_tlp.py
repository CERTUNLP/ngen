"""
Django Tlp filter tests. Tests search_fields and filterset_class.
"""
import datetime
import pytz
from django.utils import timezone
from ngen.tests.filters.base_filter_test import BaseFilterTest
from ngen.filters import TlpFilter
from ngen.models import Tlp


class TlpFilterTest(BaseFilterTest):
    """
    Tlp filter test class.
    """

    fixtures = ['user.json', 'priority.json']

    @classmethod
    def setUpTestData(cls):
        cls.basename = "tlp"
        super().setUpTestData()

        cls.tlp_1 = Tlp.objects.create(
            when="When one",
            why="Why one",
            information="Information one",
            description="Description one",
            encrypt=False,
            name="TLP One",
            slug="tlp_one",
            code=0
        )
        cls.tlp_1.created = timezone.datetime(2024, 1, 1, tzinfo=pytz.UTC)
        cls.tlp_1.save()

        cls.tlp_2 = Tlp.objects.create(
            when="When two",
            why="Why two",
            information="Information two",
            description="Description two",
            encrypt=True,
            name="TLP Two",
            slug="tlp_two",
            code=1
        )

        cls.tlp_3 = Tlp.objects.create(
            when="When three",
            why="Why three",
            information="Information three",
            description="Description three",
            encrypt=False,
            name="TLP Three",
            slug="tlp_three",
            code=2
        )

        cls.queryset = Tlp.objects.all()

        cls.filter = lambda query_params: TlpFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        self.authenticate()

        # Searching by name
        query = "two"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.tlp_2.id
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
            "id": self.tlp_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.tlp_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2024-01-01",
            "created_range_before": "2024-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.tlp_1])

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
            [self.tlp_1, self.tlp_2, self.tlp_3],
            ordered=False
        )
    
    def test_filter_by_when(self):
        """
        Test filter by when.
        """

        params = {
            "when__icontains": "two"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.tlp_2])

        params = {
            "when__icontains": "when"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.tlp_1, self.tlp_2, self.tlp_3], ordered=False)

    def test_filter_by_why(self):
        """
        Test filter by why.
        """

        params = {
            "why__icontains": "two"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.tlp_2])

        params = {
            "why__icontains": "why"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.tlp_1, self.tlp_2, self.tlp_3], ordered=False)

    def test_filter_by_information(self):
        """
        Test filter by information.
        """

        params = {
            "information__icontains": "two"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.tlp_2])

        params = {
            "information__icontains": "information"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.tlp_1, self.tlp_2, self.tlp_3], ordered=False)

    def test_filter_by_description(self):
        """
        Test filter by description.
        """

        params = {
            "description__icontains": "two"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.tlp_2])

        params = {
            "description__icontains": "description"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.tlp_1, self.tlp_2, self.tlp_3], ordered=False)

    def test_filter_by_encrypt(self):
        """
        Test filter by encrypt.
        """

        params = {
            "encrypt": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.tlp_2])

        params = {
            "encrypt": False
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.tlp_1, self.tlp_3], ordered=False)
    
    def test_filter_by_name(self):
        """
        Test filter by name.
        """

        params = {
            "name__icontains": "two"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.tlp_2])

        params = {
            "name__icontains": "o"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.tlp_1, self.tlp_2], ordered=False)

    def test_filter_by_slug(self):
        """
        Test filter by slug.
        """

        params = {
            "slug__icontains": "two"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.tlp_2])

        params = {
            "slug__icontains": "o"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.tlp_1, self.tlp_2], ordered=False)

    def test_filter_by_code(self):
        """
        Test filter by code.
        """

        params = {
            "code": 0
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.tlp_1])
