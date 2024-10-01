from rest_framework import serializers

from ngen import models
from ngen.serializers.common.mixins import AuditSerializerMixin


class NetworkSerializer(AuditSerializerMixin):
    children = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="network-detail"
    )
    parent = serializers.HyperlinkedRelatedField(
        many=False, read_only=True, view_name="network-detail"
    )

    class Meta:
        model = models.Network
        fields = "__all__"


class NetworkAdminNetworkSerializer(NetworkSerializer):
    children = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="networkadminnetwork-detail"
    )
    parent = serializers.HyperlinkedRelatedField(
        many=False, read_only=True, view_name="networkadminnetwork-detail"
    )

    class Meta(NetworkSerializer.Meta):
        extra_kwargs = {
            "url": {"view_name": "networkadminnetwork-detail"},
            "contacts": {"view_name": "networkadmincontact-detail"},
            "network_entity": {"view_name": "networkadminnetworkentity-detail"},
        }


class NetworkEntitySerializer(AuditSerializerMixin):
    networks = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="network-detail"
    )

    class Meta:
        model = models.NetworkEntity
        fields = "__all__"
        read_only_fields = ["slug"]


class NetworkAdminNetworkEntitySerializer(NetworkEntitySerializer):
    networks = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="networkadminnetwork-detail"
    )

    class Meta(NetworkEntitySerializer.Meta):
        extra_kwargs = {
            "url": {"view_name": "networkadminnetworkentity-detail"},
        }


class NetworkEntitySerializerReduced(serializers.HyperlinkedModelSerializer):
    networks = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="network-detail"
    )

    class Meta:
        model = models.NetworkEntity
        fields = ["url", "name", "slug", "active", "networks", "events"]


class ContactSerializer(AuditSerializerMixin):

    class Meta:
        model = models.Contact
        fields = [
            "url",
            "history",
            "created",
            "modified",
            "name",
            "username",
            "public_key",
            "type",
            "role",
            "priority",
            "user",
            "networks",
        ]


class NetworkAdminContactSerializer(ContactSerializer):
    class Meta(ContactSerializer.Meta):
        fields = [f for f in ContactSerializer.Meta.fields if f not in ["user"]]
        extra_kwargs = {
            "url": {"view_name": "networkadmincontact-detail"},
        }


class EntityMinifiedSerializer(AuditSerializerMixin):
    class Meta:
        model = models.NetworkEntity
        fields = ["url", "name"]


class ContactMinifiedSerializer(AuditSerializerMixin):
    class Meta:
        model = models.Contact
        fields = ["url", "name"]
