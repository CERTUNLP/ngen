from rest_framework import serializers
from ngen.models.communication_channel import CommunicationType


class CommunicationTypeSerializer(serializers.ModelSerializer):
    """
    CommunicationTypeSerializer class
    """

    class Meta:
        model = CommunicationType
        fields = ["id", "type"]
