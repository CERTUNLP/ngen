from ngen import models
from ngen.serializers import AuditSerializerMixin


class StateSerializer(AuditSerializerMixin):
    class Meta:
        model = models.State
        fields = '__all__'
        read_only_fields = ['slug']


class EdgeSerializer(AuditSerializerMixin):
    class Meta:
        model = models.Edge
        fields = '__all__'
