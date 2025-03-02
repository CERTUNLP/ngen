import json

from django.urls import reverse
from rest_framework import status
from ngen.tests.api.api_test_case_with_login import APITestCaseWithLogin

from ngen.models import (
    Priority,
    Tlp,
    Event,
    Taxonomy,
    Feed,
    User,
    CommunicationChannel,
    Contact,
    Network,
    NetworkEntity,
    CommunicationType,
    CommunicationChannelTypeRelation,
)


class TestCommunicationChannel(APITestCaseWithLogin):
    """
    This will handle Communication Channel API tests
    """

    fixtures = [
        "tests/contact.json",
        "tests/priority.json",
        "tests/tlp.json",
        "tests/user.json",
        "tests/feed.json",
        "tests/taxonomy.json",
        "tests/user.json",
        "tests/network_entity.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        basename = "communicationchannel"
        cls.url_list = reverse(f"{basename}-list")
        cls.url_detail = lambda pk: reverse(f"{basename}-detail", kwargs={"pk": pk})
        cls.nested_url_list = (
            lambda channelable_name, channelable_pk: f"/api/{channelable_name}/{channelable_pk}"
            "/communicationchannels/"
        )
        cls.nested_url_detail = (
            lambda channelable_name, channelable_pk, pk: f"/api/{channelable_name}/{channelable_pk}"
            f"/communicationchannels/{pk}/"
        )

        cls.priority = Priority.objects.get(slug="high")
        cls.tlp = Tlp.objects.get(slug="green")
        cls.taxonomy_1 = Taxonomy.objects.get(slug="botnet")
        cls.taxonomy_2 = Taxonomy.objects.get(slug="malware")
        cls.feed_1 = Feed.objects.get(slug="csirtamericas")
        cls.feed_2 = Feed.objects.get(slug="cert_unlp")
        cls.user_1 = User.objects.get(username="ngen")
        cls.user_2 = User.objects.create(
            username="testuser",
            password="testuser",
            email="test@example.com",
            priority=cls.priority,
        )
        cls.contact_1 = Contact.objects.get(pk=1)
        cls.contact_2 = Contact.objects.create(
            priority=cls.priority,
            name="Soporte UTN",
            username="soporte@cert.utn.edu.ar",
            type="email",
            role="administrative",
        )
        cls.contact_3 = Contact.objects.create(
            priority=cls.priority,
            name="Contacto Adicional",
            username="additional@contact.com",
            type="email",
            role="administrative",
        )
        cls.entity_1 = NetworkEntity.objects.get(pk=1)
        cls.entity_2 = NetworkEntity.objects.create(
            name="UTN",
            active=True,
        )

        cls.domain_1 = "testdomain.unlp.edu.ar"
        cls.domain_2 = "anotherdomain.utn.edu.ar"

        cls.network_1 = Network.objects.create(
            domain=cls.domain_1,
            active=True,
            type="external",
            network_entity=cls.entity_1,
        )
        cls.network_1.contacts.set([cls.contact_1])

        cls.network_2 = Network.objects.create(
            domain=cls.domain_2,
            active=True,
            type="external",
            network_entity=cls.entity_2,
        )
        cls.network_2.contacts.set([cls.contact_2])

        cls.event_1 = Event.objects.create(
            domain=cls.domain_1,
            taxonomy=cls.taxonomy_1,
            feed=cls.feed_1,
            tlp=cls.tlp,
            reporter=cls.user_1,
            notes="Some notes",
            priority=cls.priority,
        )

        cls.event_2 = Event.objects.create(
            domain=cls.domain_2,
            taxonomy=cls.taxonomy_2,
            feed=cls.feed_2,
            tlp=cls.tlp,
            reporter=cls.user_2,
            notes="Some notes",
            priority=cls.priority,
        )

        cls.affected_type = CommunicationType.objects.create(type="affected")
        cls.reporter_type = CommunicationType.objects.create(type="reporter")
        cls.intern_type = CommunicationType.objects.create(type="intern")

    def get_messages_from_response(self, response):
        """
        Helper method that returns the messages from the response
        """
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return None

    def test_communication_channel_get_list(self):
        """
        This will test successful Communication Channel GET list
        """
        communication_channels = [
            CommunicationChannel.objects.create(
                name="Test Communication Channel 1",
                message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
                channelable=self.event_1,
            ),
            CommunicationChannel.objects.create(
                name="Test Communication Channel 2",
                message_id="acb3b8b7-347e-4f6b-8b9e-689f33f4b123",
                channelable=self.event_2,
            ),
        ]

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(communication_channels))
        self.assertEqual(
            response.data["results"][0]["name"], communication_channels[0].name
        )
        self.assertEqual(
            response.data["results"][1]["name"], communication_channels[1].name
        )

    def test_communication_channel_get_detail(self):
        """
        This will test successful Communication Channel GET detail
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        response = self.client.get(self.url_detail(communication_channel.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], communication_channel.name)

    def test_communication_channel_put(self):
        """
        This will test successful Communication Channel PUT
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        channel_type_relation = CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.affected_type,
        )

        json_data = {
            "name": "New name",
            "message_id": "acb3b8b7-347e-4f6b-8b9e-689f33f4b123",
            "communication_types": [self.reporter_type.pk],
            "additional_contacts": ["new@contact.com"],
        }

        response = self.client.put(
            self.url_detail(communication_channel.pk), data=json_data
        )

        communication_channel.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(communication_channel.name, "New name")
        self.assertEqual(communication_channel.communication_types.count(), 1)
        self.assertTrue(
            communication_channel.communication_types.contains(self.reporter_type)
        )
        self.assertEqual(len(communication_channel.additional_contacts), 1)
        self.assertEqual(
            communication_channel.additional_contacts[0],
            json_data["additional_contacts"][0],
        )
        with self.assertRaises(CommunicationChannelTypeRelation.DoesNotExist):
            CommunicationChannelTypeRelation.objects.get(id=channel_type_relation.id)

    def test_communication_channel_put_without_communication_types(self):
        """
        This will test unsuccessful Communication Channel PUT without communication_types
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        json_data = {"name": "New name"}

        response = self.client.put(
            self.url_detail(communication_channel.pk), data=json_data
        )

        communication_channel.refresh_from_db()
        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response_messages["communication_types"])
        self.assertEqual(communication_channel.name, "Test Communication Channel 1")

    def test_communication_channel_put_with_empty_communication_types(self):
        """
        This will test unsuccessful Communication Channel PUT with empty communication_types
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        json_data = {"name": "New name", "communication_types": []}

        response = self.client.put(
            self.url_detail(communication_channel.pk), data=json_data
        )

        communication_channel.refresh_from_db()
        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response_messages["communication_types"])
        self.assertEqual(communication_channel.name, "Test Communication Channel 1")

    def test_communication_channel_put_with_non_existent_communication_types(self):
        """
        This will test unsuccessful Communication Channel PUT
        with non existent communication_types
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.intern_type,
        )

        json_data = {
            "name": "New name",
            "communication_types": [
                self.affected_type.pk,
                7777,
                self.reporter_type.pk,
                9999,
            ],
        }

        response = self.client.put(
            self.url_detail(communication_channel.pk), data=json_data
        )

        communication_channel.refresh_from_db()
        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Communication Types with IDs [7777, 9999] not found",
            response_messages["communication_types"],
        )
        self.assertEqual(communication_channel.name, "Test Communication Channel 1")
        self.assertEqual(communication_channel.communication_types.count(), 1)
        self.assertTrue(
            communication_channel.communication_types.contains(self.intern_type)
        )

    def test_communication_channel_patch(self):
        """
        This will test successful Communication Channel PATCH
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
            additional_contacts=["some@contact.com"],
        )

        channel_type_relation = CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.affected_type,
        )

        json_data = {
            "name": "New name",
            "communication_types": [self.reporter_type.pk],
            "additional_contacts": ["new@contact.com"],
        }

        response = self.client.patch(
            self.url_detail(communication_channel.pk), data=json_data
        )

        communication_channel.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(communication_channel.name, "New name")
        self.assertEqual(communication_channel.communication_types.count(), 1)
        self.assertTrue(
            communication_channel.communication_types.contains(self.reporter_type)
        )
        self.assertEqual(
            communication_channel.additional_contacts,
            json_data["additional_contacts"],
        )
        with self.assertRaises(CommunicationChannelTypeRelation.DoesNotExist):
            CommunicationChannelTypeRelation.objects.get(id=channel_type_relation.id)

    def test_communication_channel_patch_with_non_existent_communication_types(self):
        """
        This will test unsuccessful Communication Channel PATCH
        with non existent communication_types
        """
        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.intern_type,
        )

        json_data = {
            "name": "New name",
            "communication_types": [
                self.affected_type.pk,
                7777,
                self.reporter_type.pk,
                9999,
            ],
        }

        response = self.client.patch(
            self.url_detail(communication_channel.pk), data=json_data
        )

        communication_channel.refresh_from_db()
        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Communication Types with IDs [7777, 9999] not found",
            response_messages["communication_types"],
        )
        self.assertEqual(communication_channel.name, "Test Communication Channel 1")
        self.assertEqual(communication_channel.communication_types.count(), 1)
        self.assertTrue(
            communication_channel.communication_types.contains(self.intern_type)
        )

    def test_communication_channel_delete(self):
        """
        This will test successful Communication Channel DELETE
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        channel_type_relation = CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.affected_type,
        )

        communication_channel_pk = communication_channel.pk

        response = self.client.delete(self.url_detail(communication_channel_pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(CommunicationChannel.DoesNotExist):
            CommunicationChannel.objects.get(pk=communication_channel_pk)
        with self.assertRaises(CommunicationChannelTypeRelation.DoesNotExist):
            CommunicationChannelTypeRelation.objects.get(id=channel_type_relation.id)

    # Nested communication channel endpoints tests under channelable

    def test_nested_communication_channel_get_list(self):
        """
        This will test successful nested Communication Channel GET list
        """
        communication_channels = [
            CommunicationChannel.objects.create(
                name="Test Communication Channel 1",
                message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
                channelable=self.event_1,
            ),
            CommunicationChannel.objects.create(
                name="Test Communication Channel 2",
                message_id="acb3b8b7-347e-4f6b-8b9e-689f33f4b123",
                channelable=self.event_2,
            ),
            CommunicationChannel.objects.create(
                name="Test Communication Channel 2",
                message_id="acb3b8b7-347e-4f6b-8b9e-689f33f4b123",
                channelable=self.event_1,
            ),
        ]

        response = self.client.get(self.nested_url_list("event", self.event_1.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(
            response.data["results"][0]["name"], communication_channels[0].name
        )
        self.assertEqual(
            response.data["results"][1]["name"], communication_channels[1].name
        )

    def test_nested_communication_channel_get_list_pagination(self):
        """
        This will test successful nested Communication Channel GET list pagination
        """
        for i in range(12):
            CommunicationChannel.objects.create(
                name=f"Test Communication Channel {i}",
                message_id=f"{i}",
                channelable=self.event_1,
            )

        response = self.client.get(self.nested_url_list("event", self.event_1.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])

    def test_nested_communication_channel_get_detail(self):
        """
        This will test successful nested Communication Channel GET detail
        """
        communication_channels = [
            CommunicationChannel.objects.create(
                name="Test Communication Channel 1",
                message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
                channelable=self.event_1,
            ),
            CommunicationChannel.objects.create(
                name="Test Communication Channel 2",
                message_id="acb3b8b7-347e-4f6b-8b9e-689f33f4b123",
                channelable=self.event_2,
            ),
        ]

        response = self.client.get(
            self.nested_url_detail(
                "event", self.event_1.pk, communication_channels[0].pk
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], communication_channels[0].name)

    def test_nested_communication_channel_post(self):
        """
        This will test successful nested Communication Channel POST
        """

        json_data = {
            "name": "Test Communication Channel 1",
            "message_id": "f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            "communication_types": [self.affected_type.pk],
            "additional_contacts": ["some@contact.com"],
        }

        response = self.client.post(
            self.nested_url_list("event", self.event_1.pk), data=json_data
        )

        communication_channel = CommunicationChannel.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommunicationChannel.objects.count(), 1)
        self.assertEqual(communication_channel.name, json_data["name"])
        self.assertEqual(communication_channel.message_id, json_data["message_id"])
        self.assertEqual(communication_channel.channelable, self.event_1)
        self.assertEqual(communication_channel.communication_types.count(), 1)
        self.assertTrue(
            communication_channel.communication_types.contains(self.affected_type)
        )
        self.assertEqual(
            communication_channel.additional_contacts, json_data["additional_contacts"]
        )

    def test_nested_communication_channel_post_without_communication_types(self):
        """
        This will test unsuccessful nested Communication Channel POST without communication_types
        """

        json_data = {
            "name": "Test Communication Channel 1",
            "message_id": "f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
        }

        response = self.client.post(
            self.nested_url_list("event", self.event_1.pk), data=json_data
        )

        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response_messages["communication_types"])

    def test_nested_communication_channel_post_with_empty_communication_types(self):
        """
        This will test unsuccessful nested Communication Channel POST
        with empty communication_types
        """
        json_data = {
            "name": "Test Communication Channel 1",
            "message_id": "f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            "communication_types": [],
        }

        response = self.client.post(
            self.nested_url_list("event", self.event_1.pk), data=json_data
        )

        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response_messages["communication_types"])

    def test_nested_communication_channel_post_with_non_existent_communication_types(
        self,
    ):
        """
        This will test unsuccessful nested Communication Channel POST
        with non existent communication_types
        """

        json_data = {
            "name": "Test Communication Channel 1",
            "message_id": "f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            "communication_types": [
                self.affected_type.pk,
                7777,
                self.reporter_type.pk,
                9999,
            ],
        }

        response = self.client.post(
            self.nested_url_list("event", self.event_1.pk), data=json_data
        )

        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Communication Types with IDs [7777, 9999] not found",
            response_messages["communication_types"],
        )

    def test_nested_communication_channel_put(self):
        """
        This will test successful nested Communication Channel PUT
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
            additional_contacts=["some@contact.com"],
        )

        channel_type_relation = CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.affected_type,
        )

        json_data = {
            "name": "New name",
            "message_id": "acb3b8b7-347e-4f6b-8b9e-689f33f4b123",
            "communication_types": [self.reporter_type.pk],
            "additional_contacts": ["new@contact.com"],
        }

        response = self.client.put(
            self.nested_url_detail("event", self.event_1.pk, communication_channel.pk),
            data=json_data,
        )

        communication_channel.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(communication_channel.name, json_data["name"])
        self.assertEqual(communication_channel.communication_types.count(), 1)
        self.assertTrue(
            communication_channel.communication_types.contains(self.reporter_type)
        )
        self.assertEqual(
            communication_channel.additional_contacts, json_data["additional_contacts"]
        )
        with self.assertRaises(CommunicationChannelTypeRelation.DoesNotExist):
            CommunicationChannelTypeRelation.objects.get(id=channel_type_relation.id)

    def test_nested_communication_channel_put_without_communication_types(self):
        """
        This will test unsuccessful nested Communication Channel PUT without communication_types
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        json_data = {"name": "New name"}

        response = self.client.put(
            self.nested_url_detail("event", self.event_1.pk, communication_channel.pk),
            data=json_data,
        )

        communication_channel.refresh_from_db()
        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response_messages["communication_types"])
        self.assertEqual(communication_channel.name, "Test Communication Channel 1")

    def test_nested_communication_channel_put_with_empty_communication_types(self):
        """
        This will test unsuccessful nested Communication Channel PUT
        with empty communication_types
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        json_data = {"name": "New name", "communication_types": []}

        response = self.client.put(
            self.nested_url_detail("event", self.event_1.pk, communication_channel.pk),
            data=json_data,
        )

        communication_channel.refresh_from_db()
        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response_messages["communication_types"])
        self.assertEqual(communication_channel.name, "Test Communication Channel 1")

    def test_nested_communication_channel_put_with_non_existent_communication_types(
        self,
    ):
        """
        This will test unsuccessful nested Communication Channel PUT
        with non existent communication_types
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.intern_type,
        )

        json_data = {
            "name": "New name",
            "communication_types": [
                self.affected_type.pk,
                7777,
                self.reporter_type.pk,
                9999,
            ],
        }

        response = self.client.put(
            self.nested_url_detail("event", self.event_1.pk, communication_channel.pk),
            data=json_data,
        )

        communication_channel.refresh_from_db()
        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Communication Types with IDs [7777, 9999] not found",
            response_messages["communication_types"],
        )
        self.assertEqual(communication_channel.name, "Test Communication Channel 1")
        self.assertEqual(communication_channel.communication_types.count(), 1)
        self.assertTrue(
            communication_channel.communication_types.contains(self.intern_type)
        )

    def test_nested_communication_channel_patch(self):
        """
        This will test successful nested Communication Channel PATCH
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
            additional_contacts=["some@contact.com"],
        )

        channel_type_relation = CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.affected_type,
        )

        json_data = {
            "name": "New name",
            "communication_types": [self.reporter_type.pk],
            "additional_contacts": ["new@contact.com"],
        }

        response = self.client.patch(
            self.nested_url_detail("event", self.event_1.pk, communication_channel.pk),
            data=json_data,
        )

        communication_channel.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(communication_channel.name, json_data["name"])
        self.assertEqual(communication_channel.communication_types.count(), 1)
        self.assertTrue(
            communication_channel.communication_types.contains(self.reporter_type)
        )
        self.assertEqual(
            communication_channel.additional_contacts, json_data["additional_contacts"]
        )
        with self.assertRaises(CommunicationChannelTypeRelation.DoesNotExist):
            CommunicationChannelTypeRelation.objects.get(id=channel_type_relation.id)

    def test_nested_communication_channel_patch_with_non_existent_communication_types(
        self,
    ):
        """
        This will test unsuccessful nested Communication Channel PATCH
        with non existent communication_types
        """
        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.intern_type,
        )

        json_data = {
            "name": "New name",
            "communication_types": [
                self.affected_type.pk,
                7777,
                self.reporter_type.pk,
                9999,
            ],
        }

        response = self.client.patch(
            self.nested_url_detail("event", self.event_1.pk, communication_channel.pk),
            data=json_data,
        )

        communication_channel.refresh_from_db()
        response_messages = self.get_messages_from_response(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Communication Types with IDs [7777, 9999] not found",
            response_messages["communication_types"],
        )
        self.assertEqual(communication_channel.name, "Test Communication Channel 1")
        self.assertEqual(communication_channel.communication_types.count(), 1)
        self.assertTrue(
            communication_channel.communication_types.contains(self.intern_type)
        )

    def test_nested_communication_channel_delete(self):
        """
        This will test successful nested Communication Channel DELETE
        """

        communication_channel = CommunicationChannel.objects.create(
            name="Test Communication Channel 1",
            message_id="f4b3b8b7-347e-4f6b-8b9e-689f33f4b56c",
            channelable=self.event_1,
        )

        channel_type_relation = CommunicationChannelTypeRelation.objects.create(
            communication_channel=communication_channel,
            communication_type=self.affected_type,
        )

        response = self.client.delete(
            self.nested_url_detail("event", self.event_1.pk, communication_channel.pk)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(CommunicationChannel.DoesNotExist):
            CommunicationChannel.objects.get(pk=communication_channel.pk)
        with self.assertRaises(CommunicationChannelTypeRelation.DoesNotExist):
            CommunicationChannelTypeRelation.objects.get(id=channel_type_relation.id)
