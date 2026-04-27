from rest_framework import serializers

from ngen import models
from ngen.analyzers.registry import get_config_schema, ANALYZER_TYPE_CHOICES
from ngen.serializers.common.mixins import AuditSerializerMixin


class AnalyzerSerializer(AuditSerializerMixin):
    type = serializers.ChoiceField(choices=ANALYZER_TYPE_CHOICES)
    config = serializers.JSONField(default=dict)

    class Meta:
        model = models.Analyzer
        fields = "__all__"

    def validate(self, attrs):
        analyzer_type = attrs.get("type") or (self.instance.type if self.instance else None)
        config = attrs.get("config", {})

        schema = get_config_schema().get(analyzer_type, {})

        errors = {}
        for field, meta in schema.items():
            if meta.get("required") and not config.get(field):
                errors[field] = f"'{field}' is required for {analyzer_type} analyzer."
        if errors:
            raise serializers.ValidationError({"config": errors})

        return attrs