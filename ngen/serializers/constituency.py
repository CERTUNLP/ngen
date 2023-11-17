from rest_framework import serializers

from ngen import models
from ngen.serializers.common.mixins import AuditSerializerMixin


class NetworkSerializer(AuditSerializerMixin):
    children = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='network-detail'
    )
    parent = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='network-detail'
    )

    class Meta:
        model = models.Network
        fields = '__all__'


class NetworkEntitySerializer(AuditSerializerMixin):
    networks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='network-detail'
    )

    class Meta:
        model = models.NetworkEntity
        fields = '__all__'
        read_only_fields = ['slug']

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
        fields = '__all__'
