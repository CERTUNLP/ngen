"""
Django Unit Tests for Communication Type model
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from ngen.models import CommunicationType


class CommunicationTypeTest(TestCase):
    """
    This will handle Communication Type model tests
    """

    @classmethod
    def setUpTestData(cls):
        """
        Communication Type model test setup data
        """

        cls.affected_type = CommunicationType.objects.create(type="affected")
        cls.reporter_type = CommunicationType.objects.create(type="reporter")
        cls.intern_type = CommunicationType.objects.create(type="intern")

    def test_communication_type_creation(self):
        """
        This will test Communication Type creation
        """
        self.assertTrue(isinstance(self.affected_type, CommunicationType))
        self.assertTrue(isinstance(self.reporter_type, CommunicationType))
        self.assertTrue(isinstance(self.intern_type, CommunicationType))

        with self.assertRaises(ValidationError) as cm:
            CommunicationType.objects.create(type="wrong_type")

        self.assertEqual(
            cm.exception.args[0],
            "Invalid type. Valid options are Affected, Reporter, Intern",
        )

    def test_type(self):
        """
        This will test Communication Type type attribute
        """
        self.assertEqual(self.affected_type.type, "affected")
        self.assertEqual(self.reporter_type.type, "reporter")
        self.assertEqual(self.intern_type.type, "intern")

    def test_get_contacts_method(self):
        """
        This will test Communication Type get_contacts_method method
        """
        self.assertEqual(
            self.affected_type.get_contacts_method().__name__, "get_affected_contacts"
        )
        self.assertEqual(
            self.reporter_type.get_contacts_method().__name__, "get_reporter_contacts"
        )
        self.assertEqual(
            self.intern_type.get_contacts_method().__name__,
            "get_team_and_assigned_contacts",
        )

        self.intern_type.type = "wrong_type"
        with self.assertRaises(ValueError) as cm:
            self.intern_type.get_contacts_method()

        self.assertEqual(
            cm.exception.args[0],
            "Method for Type: 'wrong_type' not implemented",
        )
