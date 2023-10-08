"""
Base filter test class.
"""
from urllib.parse import urlparse
from rest_framework.test import APITestCase
from django.urls import reverse


class BaseFilterTest(APITestCase):
    """
    Base filter test class.
    """

    @classmethod
    def setUpTestData(cls):
        cls.url_list = reverse(f"{cls.basename}-list")
        cls.search_url = lambda query: f"{cls.url_list}?search={query}"
        cls.get_id_from_url = lambda url: int(
            urlparse(url).path.split('/')[-2])
        cls.url_login_jwt = reverse("token-create")
        cls.json_login = {"username": "ngen", "password": "ngen"}

    def authenticate(self):
        """
        Authenticate user. Only needed for SearchFilter tests.
        """

        response = self.client.post(
            self.url_login_jwt, data=self.json_login, format="json")
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + response.data["access"])
