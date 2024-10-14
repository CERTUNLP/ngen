from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import Token

from ngen.models import NetworkEntity, Network
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin


class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestNetworkEntity(APITestCaseWithLogin):
    """
    This will handle entity testcases
    """

    fixtures = [
        "tests/priority.json",
        "tests/feed.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/taxonomy.json",
        "tests/state.json",
        "tests/edge.json",
        "tests/report.json",
        "tests/network_entity.json",
        "tests/network.json",
        "tests/contact.json",
    ]

    def setUp(self):
        super().setUp()
        self.basename_list = "networkentity-list"
        self.basename_detail = "networkentity-detail"
        self.url_list = reverse(self.basename_list)

    def test_entity_post(self):
        """
        This will test successfull entity post
        """
        json_data = {
            "name": "test",
            "slug": "test",
        }
        response = self.client.post(self.url_list, data=json_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_entity_delete(self):
        """
        This will test successfull entity post
        """
        json_data = {
            "name": "test",
            "slug": "test",
        }
        obj = NetworkEntity.objects.create(**json_data)

        url = reverse(self.basename_detail, kwargs={"pk": obj.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_entity_delete_with_networks(self):
        """
        This will test successfull entity post
        """
        json_data = {"name": "test"}
        entity = NetworkEntity.objects.create(**json_data)
        network_data = {
            "cidr": "1.1.1.4",
            "type": "internal",
            "network_entity": entity,
        }
        network = Network.objects.create(**network_data)

        url = reverse(self.basename_detail, kwargs={"pk": entity.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
