from colorfield.serializers import ColorField

from ngen import models
from ngen.serializers.common.mixins import AuditSerializerMixin


class FeedSerializer(AuditSerializerMixin):
    class Meta:
        model = models.Feed
        fields = '__all__'
        read_only_fields = ['slug']


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
