from rest_framework import serializers

from ngen import models
from ngen.serializers.utils.mixins import NgenModelSerializer


class NetworkSerializer(NgenModelSerializer):
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


class NetworkEntitySerializer(NgenModelSerializer):
    networks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='network-detail'
    )

    class Meta:
        model = models.NetworkEntity
        fields = '__all__'
        read_only_fields = ['slug']


class ContactSerializer(NgenModelSerializer):
    class Meta:
        model = models.Contact
        fields = '__all__'
