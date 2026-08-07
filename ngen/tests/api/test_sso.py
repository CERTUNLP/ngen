from django.test import TestCase, override_settings

from ngen.backends import NgenOidcBackend
from ngen.models import User


class TestSsoBackend(TestCase):
    """
    This will handle how an identity of the sso provider ends up in an ngen
    account: the email is what links them, so an account that already exists is
    reused instead of duplicated
    """

    fixtures = [
        "tests/priority.json",
        "tests/user.json",
    ]

    def setUp(self):
        self.backend = NgenOidcBackend()
        self.user = User.objects.get(username="ngen")

    def claims(self, **overrides):
        return {
            "email": self.user.email,
            "email_verified": True,
            "preferred_username": "someone-else",
            "given_name": "Given",
            "family_name": "Family",
            **overrides,
        }

    def test_an_existing_user_is_linked_by_its_email(self):
        user = self.backend.authenticate(None, claims=self.claims())

        self.assertEqual(user, self.user)
        self.assertEqual(User.objects.count(), 1)

    def test_an_existing_user_is_linked_whatever_the_case_of_its_email(self):
        """
        The provider may hand the email back in another case, and that is the
        same account, not a new one
        """
        user = self.backend.authenticate(
            None, claims=self.claims(email=self.user.email.upper())
        )

        self.assertEqual(user, self.user)
        self.assertEqual(User.objects.count(), 1)

    def test_the_names_of_a_linked_user_are_updated(self):
        self.backend.authenticate(None, claims=self.claims())

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Given")
        self.assertEqual(self.user.last_name, "Family")

    def test_an_inactive_user_is_not_let_in(self):
        User.objects.filter(pk=self.user.pk).update(is_active=False)

        self.assertIsNone(self.backend.authenticate(None, claims=self.claims()))

    @override_settings(OIDC_CREATE_USER=True)
    def test_an_unknown_email_creates_a_user_that_cannot_login_with_a_password(self):
        user = self.backend.authenticate(
            None, claims=self.claims(email="newcomer@ngen.test")
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "someone-else")
        self.assertFalse(user.has_usable_password())

    @override_settings(OIDC_CREATE_USER=False)
    def test_an_unknown_email_is_refused_when_users_are_not_created(self):
        user = self.backend.authenticate(
            None, claims=self.claims(email="newcomer@ngen.test")
        )

        self.assertIsNone(user)
        self.assertEqual(User.objects.count(), 1)

    def test_claims_without_an_email_are_refused(self):
        claims = self.claims()
        del claims["email"]

        self.assertFalse(self.backend.verify_claims(claims))
        self.assertIsNone(self.backend.authenticate(None, claims=claims))

    def test_an_unverified_email_is_refused(self):
        claims = self.claims(email_verified=False)

        self.assertFalse(self.backend.verify_claims(claims))
        self.assertIsNone(self.backend.authenticate(None, claims=claims))

    @override_settings(OIDC_REQUIRED_GROUP="ngen-users")
    def test_a_required_group_is_asked_for(self):
        self.assertFalse(self.backend.verify_claims(self.claims(groups=["other"])))
        self.assertFalse(self.backend.verify_claims(self.claims()))

    @override_settings(OIDC_REQUIRED_GROUP="ngen-users")
    def test_a_required_group_is_read_the_way_keycloak_writes_it(self):
        """
        Keycloak hands the groups back with a leading slash
        """
        self.assertTrue(self.backend.verify_claims(self.claims(groups=["/ngen-users"])))
        self.assertTrue(self.backend.verify_claims(self.claims(groups=["ngen-users"])))

    def test_the_email_of_a_linked_user_is_not_updated_onto_another_one(self):
        taken = User.objects.create_user(
            username="taken", email="taken@ngen.test", password="password"
        )

        self.backend.update_user(self.user, self.claims(email=taken.email))

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, taken.email)
