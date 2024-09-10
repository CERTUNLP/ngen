from datetime import timedelta

from constance.test import override_config
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import Token

from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin


class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TestConstance(APITestCaseWithLogin):
    """
    This will handle constance testcases
    """

    fixtures = ["priority.json", "user.json"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        basename = "constance"
        cls.url_list = reverse(f"{basename}-list")
        cls.url_detail = lambda key: reverse(f"{basename}-detail", kwargs={"key": key})
        cls.team_email = "test@test.com"

    def test_constance_get(self):
        """
        This will test successfull constance get
        """
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertGreaterEqual(response.data["count"], 1)

    @override_config(TEAM_ABUSE="abuse@ngen.com")
    def test_constance_get_team_abuse(self):
        """
        This will test successfull constance get team email
        """
        response = self.client.get(self.url_detail(key="TEAM_ABUSE"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data["key"], "TEAM_ABUSE")
        self.assertEqual(response.data["value"], "abuse@ngen.com")
        self.assertEqual(response.data["value_type"], "str")
        self.assertContains(response.data["help_text"], "CSIRT abuse email")
        self.assertEqual(response.data["default"], "abuse@ngen.com")

    @override_config(TEAM_EMAIL="team@ngen.com")
    def test_constance_post(self):
        """
        This will test error constance post
        """
        response = self.client.post(
            self.url_detail(key="TEAM_EMAIL"), {"value": "test"}
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @override_config(TEAM_EMAIL="test_new_put@test.com")
    def test_constance_put(self):
        """
        This will test sucessfull constance put with get param
        """
        new_value = "test_new_put@test.com"
        response = self.client.put(
            self.url_detail(key="TEAM_EMAIL"), {"value": new_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url_detail(key="TEAM_EMAIL"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["value"], new_value)

    @override_config(TEAM_EMAIL="test_new_patch@test.com")
    def test_constance_patch(self):
        """
        This will test sucessfull constance patch with get param
        """
        new_value = "test_new_patch@test.com"
        # url = reverse(self.url_detail(key='TEAM_EMAIL'))
        response = self.client.patch(
            self.url_detail(key="TEAM_EMAIL"), {"value": new_value}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url_detail(key="TEAM_EMAIL"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["value"], new_value)

    @override_config(TEAM_EMAIL="test_new_patch@test.com")
    def test_constance_delete(self):
        """
        This will test error constance delete
        """
        response = self.client.delete(self.url_detail(key="TEAM_EMAIL"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_constance_get_invalid_key(self):
        """
        This will test error constance get invalid key with get param
        """
        response = self.client.get(self.url_detail(key="TEAM_EMAIL_INVALID"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_constance_get_invalid_key_post(self):
        """
        This will test error constance get invalid key with post and get param
        """
        response = self.client.post(
            self.url_detail(key="TEAM_EMAIL_INVALID"), {"value": "test"}
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_constance_get_invalid_key_put(self):
        """
        This will test error constance get invalid key with put and get param
        """
        response = self.client.put(
            self.url_detail(key="TEAM_EMAIL_INVALID"), {"value": "test"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_constance_get_invalid_key_patch(self):
        """
        This will test error constance get invalid key with patch and get param
        """
        response = self.client.patch(
            self.url_detail(key="TEAM_EMAIL_INVALID"), {"value": "test"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_constance_get_invalid_key_delete(self):
        """
        This will test error constance get invalid key with delete and get param
        """
        response = self.client.delete(self.url_detail(key="TEAM_EMAIL_INVALID"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
