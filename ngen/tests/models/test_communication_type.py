"""
Django Unit Tests for Communication Type model
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from ngen.models import (
    Tlp,
    Priority,
    CaseTemplate,
    State,
    Case,
    CommunicationType,
    Event,
    Taxonomy,
    Feed,
    User,
    Network,
    NetworkEntity,
    Contact,
)


class CommunicationTypeTest(TestCase):
    """
    This will handle Communication Type model tests
    """

    fixtures = [
        "priority.json",
        "tlp.json",
        "user.json",
        "state.json",
        "feed.json",
        "taxonomy.json",
        "case_template.json",
        "contact.json",
        "network_entity.json",
        "feed.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """
        Communication Type model test setup data
        """

        cls.priority = Priority.objects.get(slug="high")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.state = State.objects.get(slug="open")
        cls.case_template = CaseTemplate.objects.get(pk=1)
        cls.taxonomy = Taxonomy.objects.get(slug="botnet")
        cls.feed = Feed.objects.get(slug="csirtamericas")
        cls.user = User.objects.get(username="ngen")
        cls.contact = Contact.objects.get(pk=1)
        cls.entity = NetworkEntity.objects.get(pk=1)
        cls.domain = "testdomain.unlp.edu.ar"

        cls.network = Network.objects.create(
            domain=cls.domain, active=True, type="external", network_entity=cls.entity
        )
        cls.network.contacts.set([cls.contact])

        cls.event = Event.objects.create(
            domain=cls.domain,
            taxonomy=cls.taxonomy,
            feed=cls.feed,
            tlp=cls.tlp,
            reporter=cls.user,
            notes="Some notes",
            priority=cls.priority,
        )

        cls.case = Case.objects.create(
            priority=cls.priority,
            tlp=cls.tlp,
            casetemplate_creator=cls.case_template,
            state=cls.state,
            name="Test Case",
        )

        cls.case.events.set([cls.event])

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
            self.intern_type.get_contacts_method().__name__, "get_internal_contacts"
        )

        self.intern_type.type = "wrong_type"
        with self.assertRaises(ValueError) as cm:
            self.intern_type.get_contacts_method()

        self.assertEqual(
            cm.exception.args[0],
            "Method for Type: 'wrong_type' not implemented",
        )
