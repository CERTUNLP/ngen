"""
Base filter test class.
"""

from urllib.parse import urlparse

from django.urls import reverse

from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin


class BaseFilterTest(APITestCaseWithLogin):
    """
    Base filter test class.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_list = reverse(f"{cls.basename}-list")
        cls.search_url = lambda query: f"{cls.url_list}?search={query}"
        cls.get_id_from_url = lambda url: int(urlparse(url).path.split("/")[-2])
