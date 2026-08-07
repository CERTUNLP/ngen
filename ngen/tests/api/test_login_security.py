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


class TestRefreshCookie(APITestCase):
    """
    This will handle the cookie that holds the refresh token, which is the one
    thing of the login that the browser keeps
    """

    fixtures = [
        "tests/priority.json",
        "tests/user.json",
    ]

    def setUp(self):
        cache.clear()

    @override_settings(DEBUG=False)
    def test_the_refresh_cookie_is_not_handed_over_in_the_open(self):
        response = self.client.post(
            reverse("ctoken-create"), data={"username": "ngen", "password": "ngen"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cookie = response.cookies["refresh_token"]
        self.assertTrue(cookie["httponly"])
        self.assertTrue(cookie["secure"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["path"], reverse("ctoken-refresh"))

    @override_settings(DEBUG=False)
    def test_the_refresh_cookie_does_not_outlive_its_token(self):
        response = self.client.post(
            reverse("ctoken-create"), data={"username": "ngen", "password": "ngen"}
        )

        from django.conf import settings

        self.assertEqual(
            int(response.cookies["refresh_token"]["max-age"]),
            int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        )

    def test_the_refresh_token_is_not_in_the_body(self):
        response = self.client.post(
            reverse("ctoken-create"), data={"username": "ngen", "password": "ngen"}
        )

        self.assertNotIn("refresh", response.data)


@override_settings(
    OIDC_ENABLED=True,
    OIDC_RP_CLIENT_ID="ngen",
    OIDC_RP_CLIENT_SECRET="secret",
    OIDC_OP_AUTHORIZATION_ENDPOINT="https://sso.test/auth",
    OIDC_REDIRECT_URL="http://testserver",
)
class TestSsoFlow(APITestCase):
    """
    This will handle the login of the sso being the one that was started by this
    browser and answered by the provider for it
    """

    fixtures = [
        "tests/priority.json",
        "tests/user.json",
    ]

    def setUp(self):
        cache.clear()
        self.url_login = reverse("sso-login")
        self.url_callback = reverse("sso-callback")

    def start(self):
        response = self.client.get(self.url_login)
        query = response.url.split("?", 1)[1]
        from urllib.parse import parse_qs

        return response, {k: v[0] for k, v in parse_qs(query).items()}

    def test_the_authorization_request_asks_for_a_code_only_this_login_can_use(self):
        response, params = self.start()

        self.assertEqual(params["code_challenge_method"], "S256")
        self.assertTrue(params["code_challenge"])
        self.assertTrue(params["nonce"])
        self.assertEqual(response.cookies["sso_state"].value, params["state"])
        self.assertTrue(response.cookies["sso_state"]["httponly"])

    def test_a_callback_from_another_browser_is_refused(self):
        """
        An attacker can start a login and hand the finished callback to someone
        else, who would land inside the attacker's account
        """
        _, params = self.start()
        self.client.cookies.pop("sso_state")

        response = self.client.get(
            self.url_callback, {"code": "whatever", "state": params["state"]}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_a_state_that_was_never_started_is_refused(self):
        self.client.cookies["sso_state"] = "made-up"

        response = self.client.get(
            self.url_callback, {"code": "whatever", "state": "made-up"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("ngen.views.sso.SsoCallbackView._verify_id_token")
    @patch("ngen.views.sso.SsoCallbackView._get_jwks", return_value={})
    @patch("ngen.views.sso.SsoCallbackView._get_userinfo", return_value={})
    @patch("ngen.views.sso.SsoCallbackView._exchange_code")
    def test_a_token_that_answers_another_login_is_refused(
        self, exchange, userinfo, jwks, verify
    ):
        _, params = self.start()
        exchange.return_value = {"id_token": "token", "access_token": "access"}
        verify.return_value = {"email": "ngen@ngen.com", "nonce": "another-login"}

        response = self.client.get(
            self.url_callback, {"code": "whatever", "state": params["state"]}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("ngen.views.sso.SsoCallbackView._verify_id_token")
    @patch("ngen.views.sso.SsoCallbackView._get_jwks", return_value={})
    @patch("ngen.views.sso.SsoCallbackView._get_userinfo", return_value={})
    @patch("ngen.views.sso.SsoCallbackView._exchange_code")
    def test_the_code_of_the_login_is_given_back_in_the_fragment(
        self, exchange, userinfo, jwks, verify
    ):
        """
        A query string ends up in the history of the browser and in the referer
        of whatever the page loads, and this code is worth a session
        """
        _, params = self.start()
        code_verifier = cache.get(f"sso_state_{params['state']}")["code_verifier"]
        exchange.return_value = {"id_token": "token", "access_token": "access"}
        verify.return_value = {"email": "ngen@ngen.com", "nonce": params["nonce"]}

        response = self.client.get(
            self.url_callback, {"code": "whatever", "state": params["state"]}
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("#code=", response.url)
        self.assertNotIn("?code=", response.url)
        # And the code was exchanged with the proof that this login started it
        self.assertEqual(exchange.call_args.args[2], code_verifier)
