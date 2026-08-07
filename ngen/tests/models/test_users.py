import importlib

from django.core.exceptions import ValidationError
from django.test import TestCase

from ngen.models import User

migration = importlib.import_module("ngen.migrations.0038_user_email_unique")


class UserEmailTest(TestCase):
    """
    This will handle the email being the identity of a user
    """

    fixtures = [
        "tests/priority.json",
        "tests/user.json",
    ]

    def setUp(self):
        self.user = User.objects.get(username="ngen")

    def test_email_is_stored_without_its_case(self):
        user = User.objects.create_user(
            username="mixed", email="Mixed.Case@Ngen.Test", password="password"
        )

        self.assertEqual(user.email, "mixed.case@ngen.test")

    def test_email_cannot_be_empty(self):
        with self.assertRaises(ValidationError) as raised:
            User.objects.create_user(username="noemail", password="password")

        self.assertIn("email", raised.exception.message_dict)

    def test_email_cannot_be_repeated(self):
        with self.assertRaises(ValidationError) as raised:
            User.objects.create_user(
                username="clone", email=self.user.email, password="password"
            )

        self.assertIn("email", raised.exception.message_dict)

    def test_email_cannot_be_repeated_in_another_case(self):
        """
        A different case is the same email, and it has to be refused as a
        validation error and not as an integrity error of the database
        """
        with self.assertRaises(ValidationError) as raised:
            User.objects.create_user(
                username="clone", email=self.user.email.upper(), password="password"
            )

        self.assertIn("email", raised.exception.message_dict)


class UserEmailMigrationTest(TestCase):
    """
    This will handle what the migration does to the emails that could not exist
    once they are unique: the duplicated ones and the missing ones
    """

    def test_a_free_email_is_left_alone(self):
        taken = set()

        self.assertEqual(migration._free_email("one@ngen.test", taken), "one@ngen.test")

    def test_a_duplicated_email_keeps_its_domain(self):
        taken = {"one@ngen.test"}

        result = migration._free_email("one@ngen.test", taken)

        self.assertNotEqual(result, "one@ngen.test")
        self.assertTrue(result.startswith("one"))
        self.assertTrue(result.endswith("@ngen.test"))

    def test_a_rewritten_email_is_free_too(self):
        """
        The number is random, so the variation it lands on has to be checked
        against the ones already given out
        """
        taken = {"one@ngen.test"} | {
            f"one{number}@ngen.test" for number in range(1000, 9999)
        }

        result = migration._free_email("one@ngen.test", taken)

        self.assertEqual(result, "one9999@ngen.test")

    def test_a_user_without_an_email_gets_a_placeholder(self):
        user = User(pk=7, username="someone")

        self.assertEqual(migration._placeholder_email(user), "someone@ngen.invalid")

    def test_a_placeholder_drops_what_an_email_cannot_hold(self):
        """
        A username may hold characters an address cannot, and a user whose name
        leaves nothing usable still needs an address of its own
        """
        self.assertEqual(
            migration._placeholder_email(User(pk=7, username="some@one")),
            "someone@ngen.invalid",
        )
        self.assertEqual(
            migration._placeholder_email(User(pk=7, username="@@@")),
            "user7@ngen.invalid",
        )
