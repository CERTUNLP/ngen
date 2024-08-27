from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ngen.models import User


class BaseAPITestCase(APITestCase):
    """
    This will handle login testcases
    """

    def setUp(self):
        self.user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "email@gmail.com",
            "username": "johnuser",
            "password": "password",
        }
        self.url = reverse("token-create")
        User.objects.create_user(**self.user_data)

    def get_token(self, username=None, password=None, access=True):
        username = self.username if (username is None) else username
        password = self.password if (password is None) else password

        url = reverse(
            "token-create"
        )  # path/url where of API where you get the access token
        resp = self.client.post(
            url, {"username": username, "password": password}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in resp.data)
        self.assertTrue("refresh" in resp.data)
        token = resp.data["access"] if access else resp.data["refresh"]
        return token

    def api_authentication(self, token=None):
        token = self.token if (token is None) else token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
