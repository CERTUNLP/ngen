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

    canalizable = serializers.SerializerMethodField
    communication_types = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = models.CommunicationChannel
        exclude = ["content_type", "object_id"]

    def get_canalizable(self, obj):
        return GenericRelationField().generic_detail_link(
            obj.canalizable, self.context.get("request")
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

    def create(self, validated_data):
        """
        Overwrite create to add communication channel types
        """
        type_ids = validated_data.pop("communication_types", [])

        type_ids_not_found = [
            type_id
            for type_id in type_ids
            if type_id
            not in models.CommunicationType.objects.values_list("id", flat=True)
        ]
        if type_ids_not_found:
            raise serializers.ValidationError(
                f"Communication Types with IDs {type_ids_not_found} not found"
            )

        communication_channel = super().create(validated_data)

        for type_id in type_ids:
            models.CommunicationChannelTypeRelation.objects.create(
                communication_channel=communication_channel,
                communication_type_id=type_id,
            )

        return communication_channel

    def update(self, instance, validated_data):
        """
        Overwrite update to add or remove communication channel types
        """
        type_ids = validated_data.pop("communication_types", [])

        type_ids_not_found = [
            type_id
            for type_id in type_ids
            if type_id
            not in models.CommunicationType.objects.values_list("id", flat=True)
        ]
        if type_ids_not_found:
            raise serializers.ValidationError(
                f"Communication Types with IDs {type_ids_not_found} not found"
            )

        instance = super().update(instance, validated_data)

        models.CommunicationChannelTypeRelation.objects.filter(
            communication_channel=instance
        ).exclude(communication_type__id__in=type_ids).delete()

        for type_id in type_ids:
            models.CommunicationChannelTypeRelation.objects.get_or_create(
                communication_channel=instance,
                communication_type_id=type_id,
            )

        return instance
