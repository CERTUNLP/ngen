from ngen import models
from rest_framework import serializers


class EmailMessageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.EmailMessage
        fields = "__all__"
