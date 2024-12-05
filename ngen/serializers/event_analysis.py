from ngen import models
from ngen.serializers import AuditSerializerMixin

class EventAnalysisSerializer(AuditSerializerMixin):
    class Meta:
        model = models.EventAnalysis
        fields = "__all__"

