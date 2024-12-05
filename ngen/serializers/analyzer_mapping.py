from ngen import models
from ngen.serializers import AuditSerializerMixin

class AnalyzerMappingSerializer(AuditSerializerMixin):
    class Meta:
        model = models.AnalyzerMapping
        fields = "__all__"

