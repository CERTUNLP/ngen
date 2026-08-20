from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ngen.models import User


class HealthEndpointTestCase(APITestCase):
    """Tests for the liveness endpoint used by the frontend connection indicator"""

    fixtures = ["tests/priority.json"]

    def setUp(self):
        self.url = reverse("health")

    def test_health_returns_200_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_returns_200_for_authenticated_user(self):
        User.objects.create_user(
            username="testuser", password="password", email="test@ngen.test"
        )
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
