from rest_framework.test import APITestCase, APIClient
from django.urls import reverse


class APITestCaseWithLogin(APITestCase):
    """
    This class is used to authenticate the APIClient in the setUpTestData method
    so that the auth process is not repeated in every test case.
    The setUp() method of this class replaces
    the default APITestCase client with the authenticated one,
    because the client attribute cannot be modified in a class method.

    If setUpTestData() or setUp() are overridden in a subclass,
    their respective super() methods must be called.
    e.g.: super().setUpTestData() or super().setUp()
    """

    @classmethod
    def setUpTestData(cls):
        """
        Save authenticated client in 'custom_client' attribute
        """
        cls.url_login_jwt = reverse("token-create")
        cls.json_login = {"username": "ngen", "password": "ngen"}
        cls.custom_client = APIClient()

        response = cls.custom_client.post(
            cls.url_login_jwt, data=cls.json_login, format="json"
        )

        token = response.data.get("access")

        cls.custom_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def setUp(self):
        """
        Assigns authenticated 'custom_client' to APIClient 'client' attribute
        """
        try:
            self.client = self.custom_client
        except AttributeError as exc:
            raise AttributeError(
                "'custom_client' not found, did you override setUpTestData method without calling super().setUpTestData()?"
            ) from exc
