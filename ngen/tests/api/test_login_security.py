from unittest.mock import patch

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ngen.models import User


class TestLoginAttempts(APITestCase):
    """
    This will handle a password not being free to guess: every way in ends up
    calling authenticate(), so the count is kept there
    """

    fixtures = [
        "tests/priority.json",
        "tests/user.json",
    ]

    def setUp(self):
        cache.clear()
        self.url = reverse("token-create")
        self.password = "Passw0rd!x"
        self.user = User.objects.create_user(
            username="attempts",
            email="attempts@ngen.test",
            password=self.password,
        )

    def login(self, password, identifier=None, **extra):
        return self.client.post(
            self.url,
            data={"username": identifier or self.user.email, "password": password},
            **extra,
        )

    def fail_until_locked(self, **extra):
        for attempt in range(10):
            self.login(f"wrong{attempt}", **extra)

    def test_the_right_password_stops_working_after_enough_failures(self):
        self.assertEqual(self.login(self.password).status_code, status.HTTP_200_OK)

        self.fail_until_locked()

        self.assertEqual(
            self.login(self.password).status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_the_count_is_kept_per_account(self):
        """
        Otherwise anyone could lock an account out of its owner, or lock a whole
        office out by failing from its address
        """
        self.fail_until_locked()

        response = self.client.post(
            self.url, data={"username": "ngen", "password": "ngen"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_the_count_is_kept_per_address(self):
        self.fail_until_locked(REMOTE_ADDR="10.0.0.1")

        response = self.login(self.password, REMOTE_ADDR="10.0.0.2")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_the_username_is_counted_as_the_email_is(self):
        self.fail_until_locked()

        self.assertEqual(
            self.login(self.password, identifier="attempts").status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_a_login_that_works_clears_the_count(self):
        for attempt in range(9):
            self.login(f"wrong{attempt}")

        self.assertEqual(self.login(self.password).status_code, status.HTTP_200_OK)

        for attempt in range(9):
            self.login(f"wrong{attempt}")
        self.assertEqual(self.login(self.password).status_code, status.HTTP_200_OK)

    @override_settings(LOGIN_MAX_ATTEMPTS=0)
    def test_the_limit_can_be_turned_off(self):
        self.fail_until_locked()

        self.assertEqual(self.login(self.password).status_code, status.HTTP_200_OK)

    # DRF reads the rates once, when it is imported, so overriding the setting
    # afterwards changes nothing: the table it kept is what has to be patched
    @patch.dict(
        "rest_framework.throttling.SimpleRateThrottle.THROTTLE_RATES",
        {"login": "3/min"},
    )
    def test_asking_too_often_is_refused_before_anything_else(self):
        """
        The counter is per account, so the rate is what keeps a list of accounts
        from being tried one attempt each
        """
        for attempt in range(3):
            self.login(f"wrong{attempt}", identifier=f"someone{attempt}@ngen.test")

        response = self.login("wrong", identifier="another@ngen.test")

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class TestSignup(APITestCase):
    """
    This will handle creating an account without being logged in, which is off
    unless the deployment asks for it and, when on, asks for a real password
    """

    fixtures = [
        "tests/priority.json",
        "tests/user.json",
    ]

    def setUp(self):
        cache.clear()
        self.url = reverse("register-list")
        self.data = {
            "username": "newcomer",
            "email": "newcomer@ngen.test",
            "password": "Passw0rd!x",
        }

    def test_signing_up_is_refused_by_default(self):
        response = self.client.post(self.url, data=self.data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(username="newcomer").exists())

    @override_settings(ALLOW_SIGNUP=True)
    def test_signing_up_works_when_it_is_asked_for(self):
        response = self.client.post(self.url, data=self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    @override_settings(ALLOW_SIGNUP=True)
    def test_signing_up_asks_for_the_same_password_the_users_page_asks_for(self):
        response = self.client.post(self.url, data={**self.data, "password": "1234"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(username="newcomer").exists())
