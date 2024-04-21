"""
Django User filter tests. Tests search_fields and filterset_class.
"""
import datetime

import pytz
from django.utils import timezone

from ngen.filters import UserFilter
from ngen.models import User
from ngen.tests.filters.base_filter_test import BaseFilterTest


class UserFilterTest(BaseFilterTest):
    """
    User filter test class.
    """

    fixtures = ['priority.json', 'user.json']

    @classmethod
    def setUpTestData(cls):
        cls.basename = "user"
        super().setUpTestData()

        cls.user_1 = User.objects.create(
            username="user_one",
            password="password",
            email="one@gmail.com",
            first_name="First Name One",
            last_name="Last Name One",
            is_staff=True,
            is_superuser=True,
            is_active=True,
            date_joined=timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC),
            last_login=timezone.datetime(2000, 1, 2, tzinfo=pytz.UTC)
        )
        cls.user_1.created = timezone.datetime(2000, 1, 1, tzinfo=pytz.UTC)
        cls.user_1.save()

        cls.user_2 = User.objects.create(
            username="user_two",
            password="password",
            email="two@gmail.com",
            first_name="First Name Two",
            last_name="Last Name Two",
            is_staff=True,
            is_superuser=False,
            is_active=False,
            date_joined=timezone.datetime(2000, 1, 2, tzinfo=pytz.UTC),
            last_login=timezone.datetime(2000, 1, 3, tzinfo=pytz.UTC)
        )

        cls.user_3 = User.objects.create(
            username="user_three",
            password="password",
            email="three@outlook.com",
            first_name="First Name Three",
            last_name="Last Name Three",
            is_staff=False,
            is_superuser=False,
            is_active=True,
            date_joined=timezone.datetime(2000, 1, 3, tzinfo=pytz.UTC),
            last_login=timezone.datetime(2000, 1, 4, tzinfo=pytz.UTC)
        )

        cls.queryset = User.objects.exclude(
            username='ngen')  # Exclude fixture user

        cls.filter = lambda query_params: UserFilter(
            query_params,
            queryset=cls.queryset
        )

    def test_search_filter(self):
        """
        SearchFilter tests.
        """

        # Searching by username
        query = "user_one"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.user_1.id
        )

        # Searching by email
        query = "gmail"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.user_1.id
        )
        self.assertEqual(
            self.get_id_from_url(response.data["results"][1]["url"]),
            self.user_2.id
        )

        # Searching by first name
        query = "first name one"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.user_1.id
        )

        # Searching by last name
        query = "last name two"
        response = self.client.get(self.search_url(query))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            self.get_id_from_url(response.data["results"][0]["url"]),
            self.user_2.id
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
            "id": self.user_1.id
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.user_1])

    def test_filter_by_created_range(self):
        """
        Test filter by created range.
        """

        params = {
            "created_range_after": "2000-01-01",
            "created_range_before": "2000-01-02"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(filtered_queryset, [self.user_1])

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
            [self.user_1, self.user_2, self.user_3],
            ordered=False
        )

    def test_filter_by_username(self):
        """
        Test filter by username.
        """

        params = {
            "username__icontains": "two"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_2])

        params = {
            "username__icontains": "o"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1, self.user_2], ordered=False)

    def test_filter_by_email(self):
        """
        Test filter by email.
        """

        params = {
            "email__icontains": "one"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1])

        params = {
            "email__icontains": "outlook"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_3], ordered=False)

    def test_filter_by_first_name(self):
        """
        Test filter by first name.
        """

        params = {
            "first_name__icontains": "one"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1])

        params = {
            "first_name__icontains": "o"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1, self.user_2], ordered=False)

    def test_filter_by_last_name(self):
        """
        Test filter by last name.
        """

        params = {
            "last_name__icontains": "one"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1])

        params = {
            "last_name__icontains": "o"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1, self.user_2], ordered=False)

    def test_filter_by_is_superuser(self):
        """
        Test filter by is superuser.
        """

        params = {
            "is_superuser": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1])

        params = {
            "is_superuser": False
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_2, self.user_3], ordered=False)

    def test_filter_by_is_staff(self):
        """
        Test filter by is staff.
        """

        params = {
            "is_staff": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1, self.user_2], ordered=False)

        params = {
            "is_staff": False
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_3])

    def test_filter_by_is_active(self):
        """
        Test filter by is active.
        """

        params = {
            "is_active": True
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1, self.user_3], ordered=False)

        params = {
            "is_active": False
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_2])

    def test_filter_by_date_joined(self):
        """
        Test filter by date joined.
        """

        params = {
            "date_joined": "2000-01-01"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_1])

    def test_filter_by_last_login(self):
        """
        Test filter by last login.
        """

        params = {
            "last_login": "2000-01-04"
        }

        filtered_queryset = self.filter(params).qs

        self.assertQuerysetEqual(
            filtered_queryset, [self.user_3])
