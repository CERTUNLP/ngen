# pylint: disable=protected-access, disable=W0223
from rest_framework import serializers

from ngen import models
from ngen.serializers.auth import UserMinifiedSerializer
from ngen.serializers.common.fields import GenericRelationField
from ngen.serializers.communication_type import CommunicationTypeSerializer
from ngen.serializers.constituency import ContactSerializer


class NetworksWithContactsSerializer(serializers.Serializer):
    """
    NetworksWithContactsSerializer class
    Contract: {cidr_or_domain: [contact1, contact2, ...]}
    """

    def to_representation(self, instance):
        key = list(instance.keys())[0]
        contacts = instance[key]
        serialized_contacts = ContactSerializer(
            contacts, context=self.context, many=True
        ).data

        return {key: serialized_contacts}


class CommunicationChannelContactsSerializer(serializers.Serializer):
    """
    NetworkContactsSerializer class
    """

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if "affected" in instance:
            representation["affected"] = NetworksWithContactsSerializer(
                instance["affected"],
                context=self.context,
                many=True,
            ).data

        if "reporter" in instance:
            representation["reporter"] = UserMinifiedSerializer(
                instance["reporter"],
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
    channel_types = serializers.SerializerMethodField(read_only=True)
    additional_contacts = serializers.ListField(
        child=serializers.EmailField(), required=False
    )

    class Meta:
        model = models.CommunicationChannel
        exclude = ["content_type", "object_id"]

    def get_channelable(self, obj):
        return GenericRelationField(read_only=True).generic_detail_link(
            obj.channelable, self.context.get("request")
        )

    def get_channel_types(self, obj):
        return CommunicationTypeSerializer(
            obj.communication_types.all(), many=True
        ).data

    def to_representation(self, instance):
        """
        Overwrite to_representation to add contacts field
        """
        representation = super().to_representation(instance)

        representation["contacts"] = CommunicationChannelContactsSerializer(
            instance.fetch_contacts(), context=self.context
        ).data

        return representation

    def validate(self, attrs):
        """
        Overwrite validate to verify IDs collections
        """
        self.validate_ids(attrs, "communication_types", models.CommunicationType)

        return attrs

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
                    field_name: f"{model._meta.verbose_name_plural.title()} "
                    f"with IDs {ids_not_found} not found"
                }
            )


class CommunicationChannelReducedSerializer(serializers.HyperlinkedModelSerializer):
    """
    CommunicationChannelReducedSerializer class
    """

    channelable = serializers.SerializerMethodField(read_only=True)
    communication_types = CommunicationTypeSerializer(many=True)

    class Meta:
        model = models.CommunicationChannel
        exclude = ["content_type", "object_id", "additional_contacts"]

    def get_channelable(self, obj):
        return GenericRelationField(read_only=True).generic_detail_link(
            obj.channelable, self.context.get("request")
        )
