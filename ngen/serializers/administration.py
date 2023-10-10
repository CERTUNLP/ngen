from colorfield.serializers import ColorField

from ngen import models
from ngen.serializers.utils.mixins import NgenModelSerializer


class FeedSerializer(NgenModelSerializer):
    class Meta:
        model = models.Feed
        fields = '__all__'
        read_only_fields = ['slug']


class TlpSerializer(NgenModelSerializer):
    color = ColorField()

    class Meta:
        model = models.Tlp
        fields = '__all__'
        read_only_fields = ['slug']


class PrioritySerializer(NgenModelSerializer):
    color = ColorField()

    class Meta:
        model = models.Priority
        fields = '__all__'
        read_only_fields = ['slug']
