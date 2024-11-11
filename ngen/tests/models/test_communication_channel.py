"""
Django Unit Tests for Communication Channel model
"""

from django.test import TestCase

from ngen.models import (
    Tlp,
    Priority,
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
        "tests/priority.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/feed.json",
        "tests/taxonomy.json",
        "tests/contact.json",
        "tests/network_entity.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """
        Communication Channel model test setup data
        """

        cls.priority = Priority.objects.get(slug="high")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.feed = Feed.objects.get(slug="csirtamericas")
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

        cls.communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=cls.event,
            additional_contacts=["some@contact.com"],
        )

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

    def test_channelable(self):
        """
        This will test Communication Channel channelable attribute
        """
        self.assertEqual(self.communication_channel.channelable, self.event)

    def test_channelable_communication_channels(self):
        """
        This will test channelable communication_channels relation
        """
        self.assertEqual(self.event.communication_channels.count(), 1)
        self.assertEqual(
            self.event.communication_channels.first(), self.communication_channel
        )

    def test_additional_contacts(self):
        """
        This will test Communication Channel additional_contacts relation
        """
        self.assertEqual(
            self.communication_channel.additional_contacts, ["some@contact.com"]
        )

    def test_communication_types(self):
        """
        This will test Communication Channel communication_types relation
        """
        self.assertEqual(self.communication_channel.communication_types.count(), 0)

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.affected_type,
        )

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.reporter_type,
        )

        self.assertEqual(self.communication_channel.communication_types.count(), 2)
        self.assertTrue(
            self.communication_channel.communication_types.contains(self.affected_type)
        )
        self.assertTrue(
            self.communication_channel.communication_types.contains(self.reporter_type)
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

        affected_domain = fetch_contacts_result["affected"][0]
        self.assertEqual(list(affected_domain.keys())[0], self.domain)
        self.assertEqual(affected_domain[self.domain], [self.contact])

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

        reporter = fetch_contacts_result["reporter"][0]
        self.assertEqual(len(fetch_contacts_result["reporter"]), 1)
        self.assertEqual(reporter, self.user)

    def test_fetch_contacts_with_intern_type(self):
        """
        This will test Communication Channel fetch_contacts method
        when the channel is associated with an intern type
        """
        self.assertEqual(self.communication_channel.fetch_contacts(), {})

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.intern_type,
        )

        fetch_contacts_result = self.communication_channel.fetch_contacts()
        self.assertTrue("intern" in fetch_contacts_result)

        intern_contacts = fetch_contacts_result["intern"]
        # Additional contacts are used as internal contacts
        self.assertEqual(intern_contacts, [])

    def test_fetch_contact_emails_with_affected_type(self):
        """
        This will test Communication Channel fetch_contact_emails method
        when the channel is associated with an affected type
        """
        self.assertEqual(self.communication_channel.fetch_contacts(), {})

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.affected_type,
        )

        fetch_contact_emails_result = self.communication_channel.fetch_contact_emails()
        affected_contact = {"name": self.contact.name, "email": self.contact.username}
        additional_contact = {"name": "some", "email": "some@contact.com"}

        expected_result = [affected_contact, additional_contact]

        self.assertEqual(fetch_contact_emails_result, expected_result)

    def test_fetch_contact_emails_with_reporter_type(self):
        """
        This will test Communication Channel fetch_contact_emails method
        when the channel is associated with a reporter type
        """
        self.assertEqual(self.communication_channel.fetch_contacts(), {})

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.reporter_type,
        )

        fetch_contact_emails_result = self.communication_channel.fetch_contact_emails()

        reporter = {
            "name": f"{self.user.first_name} {self.user.last_name}",
            "email": self.user.email,
        }
        additional_contact = {"name": "some", "email": "some@contact.com"}

        expected_result = [reporter, additional_contact]

        self.assertEqual(fetch_contact_emails_result, expected_result)

    def test_fetch_contact_emails_with_intern_type(self):
        """
        This will test Communication Channel fetch_contact_emails method
        when the channel is associated with an intern type
        """
        self.assertEqual(self.communication_channel.fetch_contacts(), {})

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=self.communication_channel,
            communication_type=self.intern_type,
        )

        fetch_contact_emails_result = self.communication_channel.fetch_contact_emails()

        expected_result = [{"name": "some", "email": "some@contact.com"}]

        self.assertEqual(fetch_contact_emails_result, expected_result)

    def test_create_channel_with_affected(self):
        """
        This will test Communication Channel create_channel_with_affected method
        """
        channel = CommunicationChannel.create_channel_with_affected(
            channelable=self.event
        )

        self.assertEqual(channel.name, "Affected Communication Channel")
        self.assertEqual(channel.channelable, self.event)
        self.assertEqual(channel.communication_types.count(), 1)
        self.assertTrue(channel.communication_types.contains(self.affected_type))
