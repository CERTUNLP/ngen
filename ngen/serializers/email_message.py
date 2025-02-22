from ngen import models
from rest_framework import serializers


class EmailMessageSerializer(serializers.ModelSerializer):
    """
    EmailMessage serializer class.
    """

    class Meta:
        model = models.EmailMessage
        fields = "__all__"
