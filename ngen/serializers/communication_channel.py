# pylint: disable=protected-access
from rest_framework import serializers
from ngen.serializers.constituency import ContactSerializer
from ngen import models
from ngen.serializers.case import EventSerializerReduced
from ngen.serializers.common.fields import GenericRelationField


class NetworksWithContactsSerializer(serializers.Serializer):
    """
    NetworksWithContactsSerializer class
    Contract: [{cidr: [contact1, contact2, ...]}, {domain: [contact1, contact2, ...]
    """

    queryset = serializers.ListField(child=serializers.DictField())

    def to_representation(self, instance):
        data = []
        for item in instance:
            key = list(item.keys())[0]
            queryset = item[key]
            serialized_queryset = ContactSerializer(
                queryset, context=self.context, many=True
            ).data
            data.append({key: serialized_queryset})
        return data


class EventWithAffectedContactsSerializer(EventSerializerReduced):
    """
    EventsWithAffectedContactsSerializer class
    """

    affected_contacts = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = [
            "url",
            "feed",
            "tlp",
            "priority",
            "taxonomy",
            "cidr",
            "domain",
            "date",
            "affected_contacts",
        ]

    def get_affected_contacts(self, obj):
        """
        Method to get affected contacts
        """
        return NetworksWithContactsSerializer(
            obj.affected_contacts, context=self.context
        ).to_representation(obj.affected_contacts)


class CommunicationChannelContactsSerializer(serializers.Serializer):
    """
    NetworkContactsSerializer class
    """

    reporter = EventSerializerReduced(required=False, many=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if "affected" in instance:
            representation["affected"] = EventWithAffectedContactsSerializer(
                instance["affected"],
                context=self.context,
                many=True,
            ).data

        return representation


class CommunicationChannelSerializer(serializers.HyperlinkedModelSerializer):
    """
    CommunicationChannelSerializer class
    """

    channelable = serializers.SerializerMethodField(read_only=True)
    communication_types = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=True
    )
    additional_contacts = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = models.CommunicationChannel
        exclude = ["content_type", "object_id"]

    def get_channelable(self, obj):
        return GenericRelationField(read_only=True).generic_detail_link(
            obj.channelable, self.context.get("request")
        )

    def to_representation(self, instance):
        """
        Overwrite to_representation to add contacts field
        """
        representation = super().to_representation(instance)

        representation["contacts"] = CommunicationChannelContactsSerializer(
            instance.fetch_contacts(), context=self.context
        ).data

        return representation

    def validate(self, data):
        """
        Overwrite validate to verify IDs collections
        """
        self.validate_ids(data, "communication_types", models.CommunicationType)
        self.validate_ids(data, "additional_contacts", models.Contact)

        return data

    def validate_ids(self, data, field_name, model):
        """
        Method to validate ids
        If any id is not found, raises a validation error
        """
        ids = data.get(field_name, [])
        ids_not_found = [
            id for id in ids if id not in model.objects.values_list("id", flat=True)
        ]
        if ids_not_found:
            raise serializers.ValidationError(
                {
                    field_name:
                    f"{model._meta.verbose_name_plural.title()} with IDs {ids_not_found} not found"
                }
            )
