from rest_framework import serializers

from ngen import models
from ngen.serializers import AuditSerializerMixin


class AnalyzerMappingSerializer(AuditSerializerMixin):
    analyzer_name = serializers.SerializerMethodField(read_only=True)
    analyzer_type = serializers.SerializerMethodField(read_only=True)

    def get_analyzer_name(self, obj):
        if obj.analyzer:
            return obj.analyzer.name
        return None

    def get_analyzer_type(self, obj):
        if obj.analyzer:
            return obj.analyzer.type
        return None

    class Meta:
        model = models.AnalyzerMapping
        fields = "__all__"