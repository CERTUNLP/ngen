"""
Django Unit Tests for Communication Channel model
"""

from django.test import TestCase

from ngen.models import (
    Tlp,
    Priority,
    CaseTemplate,
    State,
    Case,
    CommunicationChannel,
    CommunicationType,
    CommunicationChannelTypeRelation,
    Event,
    Taxonomy,
    Feed,
    User,
    Network,
    NetworkEntity,
    Contact,
)


class CommunicationChannelTest(TestCase):
    """
    This will handle Communication Channel model tests
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
        Communication Channel model test setup data
        """

        cls.priority = Priority.objects.get(slug="high")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.state = State.objects.get(slug="open")
        cls.case_template = CaseTemplate.objects.get(pk=1)
        cls.taxonomy = Taxonomy.objects.get(slug="botnet")
        cls.feed = Feed.objects.get(slug="csirtamericas")
        cls.user = User.objects.get(username="ngen")
        cls.contact = Contact.objects.get(pk=1)
        cls.contact_2 = Contact.objects.create(
            priority=cls.priority,
            name="Contacto Adicional",
            username="additional@contact.com",
            type="email",
            role="administrative",
        )
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

        cls.communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            canalizable=cls.case,
        )
        cls.communication_channel.additional_contacts.set([cls.contact_2])

        cls.affected_type = CommunicationType.objects.create(type="affected")
        cls.reporter_type = CommunicationType.objects.create(type="reporter")
        cls.intern_type = CommunicationType.objects.create(type="intern")

    def test_communication_channel_creation(self):
        """
        This will test Communication Channel creation
        """
        self.assertTrue(isinstance(self.communication_channel, CommunicationChannel))

    def test_name(self):
        """
        This will test Communication Channel name attribute
        """
        self.assertEqual(self.communication_channel.name, "Test Communication Channel")

    def test_message_id(self):
        """
        This will test Communication Channel message_id attribute
        """
        self.assertEqual(
            self.communication_channel.message_id,
            "f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
        )

    def test_canalizable(self):
        """
        This will test Communication Channel canalizable attribute
        """
        self.assertEqual(self.communication_channel.canalizable, self.case)

    def test_canalizable_communication_channels(self):
        """
        This will test canalizable communication_channels relation
        """
        self.assertEqual(self.case.communication_channels.count(), 1)
        self.assertEqual(
            self.case.communication_channels.first(), self.communication_channel
        )

    def test_additional_contacts(self):
        """
        This will test Communication Channel additional_contacts relation
        """
        self.assertEqual(self.communication_channel.additional_contacts.count(), 1)
        self.assertEqual(
            self.communication_channel.additional_contacts.first(), self.contact_2
        )

    def test_communication_types(self):
        """
        This will test Communication Channel communication_types method
        """
        self.assertEqual(self.communication_channel.communication_types().count(), 0)

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.affected_type,
        )

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.reporter_type,
        )

        self.assertEqual(self.communication_channel.communication_types().count(), 2)
        self.assertTrue(
            self.communication_channel.communication_types().contains(
                self.affected_type
            )
        )
        self.assertTrue(
            self.communication_channel.communication_types().contains(
                self.reporter_type
            )
        )

    def test_fetch_contacts_with_affected_type(self):
        """
        This will test Communication Channel fetch_contacts method
        when the channel is associated with an affected type
        """
        self.assertEqual(self.communication_channel.fetch_contacts(), {})

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.affected_type,
        )

        fetch_contacts_result = self.communication_channel.fetch_contacts()

        self.assertTrue("affected" in fetch_contacts_result)
        self.assertEqual(len(fetch_contacts_result["affected"]), 1)

        affected_event = fetch_contacts_result["affected"][0]

        self.assertEqual(affected_event, self.event)
        self.assertTrue(hasattr(affected_event, "affected_contacts"))

        affected_contacts = affected_event.affected_contacts

        self.assertEqual(len(affected_contacts), 1)

        first_affected_contact = affected_contacts[0]

        self.assertTrue(self.domain in first_affected_contact)
        self.assertEqual(len(first_affected_contact[self.domain]), 1)
        self.assertEqual(first_affected_contact[self.domain][0], self.contact)

    def test_fetch_contacts_with_reporter_type(self):
        """
        This will test Communication Channel fetch_contacts method
        when the channel is associated with a reporter type
        """
        self.assertEqual(self.communication_channel.fetch_contacts(), {})

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.reporter_type,
        )

        fetch_contacts_result = self.communication_channel.fetch_contacts()

        self.assertTrue("reporter" in fetch_contacts_result)
        self.assertEqual(len(fetch_contacts_result["reporter"]), 1)

        affected_event = fetch_contacts_result["reporter"][0]

        self.assertEqual(affected_event, self.event)
        self.assertFalse(hasattr(affected_event, "affected_contacts"))
