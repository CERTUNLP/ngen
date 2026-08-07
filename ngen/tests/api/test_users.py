from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ngen.models import User
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin


class TestLogin(APITestCase):
    """
    This will handle login testcases
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
        self.user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "email@gmail.com",
            "username": "johnuser",
            "password": "password",
        }
        self.url = reverse("token-create")
        User.objects.create_user(**self.user_data)

    def test_login(self):
        """
        This will test successfull login
        """
        post_data = {
            "username": self.user_data.get("username"),
            "password": self.user_data.get("password"),
        }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_wrong_password(self):
        """
        This will test login with wrong password
        """
        post_data = {
            "username": self.user_data.get("username"),
            "password": "wrongpassword",
        }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_wrong_username(self):
        """
        This will test login with wrong username
        """
        post_data = {
            "username": "wrongusername",
            "password": self.user_data.get("password"),
        }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_empty_password(self):
        """
        This will test login with empty password
        """
        post_data = {"username": self.user_data.get("username"), "password": ""}

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_empty_username(self):
        """
        This will test login with empty username
        """
        post_data = {"username": "", "password": self.user_data.get("password")}

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_empty_username_and_password(self):
        """
        This will test login with empty username and password
        """
        post_data = {"username": "", "password": ""}

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_invalid_username_and_password(self):
        """
        This will test login with invalid username and password
        """
        post_data = {"username": "invalidusername", "password": "invalidpassword"}

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Not implemented yet
    # def test_login_with_email(self):
    #     '''
    #     This will test login with email
    #     '''
    #     post_data = {
    #         'username' : self.user_data.get('email'),
    #         'password' : self.user_data.get('password')
    #         }

    #     response = self.client.post(self.url, data=post_data)
    #     self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)


class TestUserEmail(APITestCaseWithLogin):
    """
    This will handle the email of a user being its identity: it is required and
    no two users can share it
    """

    fixtures = [
        "tests/priority.json",
        "tests/user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_list = reverse("user-list")
        cls.url_detail = lambda pk: reverse("user-detail", kwargs={"pk": pk})
        cls.base_url = "http://testserver"
        cls.priority_url = cls.base_url + reverse("priority-detail", kwargs={"pk": 2})

    def user_data(self, **overrides):
        return {
            "username": "newuser",
            "email": "newuser@ngen.test",
            "password": "Passw0rd!",
            "priority": self.priority_url,
            **overrides,
        }

    def test_user_cannot_be_created_without_an_email(self):
        data = self.user_data()
        del data["email"]

        response = self.client.post(self.url_list, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_cannot_repeat_the_email_of_another_one(self):
        existing = User.objects.get(username="ngen")

        response = self.client.post(
            self.url_list, data=self.user_data(email=existing.email)
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_cannot_repeat_the_email_of_another_one_in_another_case(self):
        """
        The email is stored without its case, so a different case is the same
        email and has to be refused with a 400 instead of blowing up on the
        unique index
        """
        existing = User.objects.get(username="ngen")

        response = self.client.post(
            self.url_list, data=self.user_data(email=existing.email.upper())
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_email_is_stored_without_its_case(self):
        response = self.client.post(
            self.url_list, data=self.user_data(email="Mixed.Case@Ngen.Test")
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(
            User.objects.get(username="newuser").email, "mixed.case@ngen.test"
        )

    def test_user_cannot_be_updated_to_the_email_of_another_one(self):
        user = User.objects.create_user(
            username="other", email="other@ngen.test", password="password"
        )
        existing = User.objects.get(username="ngen")

        response = self.client.patch(
            self.url_detail(user.pk), data={"email": existing.email}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_keeps_its_own_email_on_an_update(self):
        """
        Its own email is not a duplicate of itself
        """
        user = User.objects.create_user(
            username="other", email="other@ngen.test", password="password"
        )

        response = self.client.patch(
            self.url_detail(user.pk),
            data={"email": user.email, "first_name": "Other"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
