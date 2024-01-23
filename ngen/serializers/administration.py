from colorfield.serializers import ColorField
from rest_framework import serializers

from ngen import models
from ngen.serializers.common.mixins import AuditSerializerMixin


class FeedSerializer(AuditSerializerMixin):
    events_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Feed
        fields = '__all__'
        read_only_fields = ['slug']

    def get_events_count(self, obj):
        return models.Event.objects.filter(feed=obj).count()


class TlpSerializer(AuditSerializerMixin):
    color = ColorField()

    class Meta:
        model = models.Tlp
        fields = '__all__'
        read_only_fields = ['slug']


class PrioritySerializer(AuditSerializerMixin):
    color = ColorField()

    class Meta:
        model = models.Priority
        fields = '__all__'
        read_only_fields = ['slug']

class FeedPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Feed
        fields = ['url', 'name']

class TlpPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tlp
        fields = ['url', 'name']        

 
class PriorityPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Priority
        fields = ['url', 'name']        

               