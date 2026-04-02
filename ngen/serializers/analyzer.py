from rest_framework import serializers

from ngen import models
from ngen.analyzers.registry import get_config_schema, ANALYZER_TYPE_CHOICES
from ngen.serializers.common.mixins import AuditSerializerMixin

SENSITIVE_PLACEHOLDER = "********"


class AnalyzerSerializer(AuditSerializerMixin):
    type = serializers.ChoiceField(choices=ANALYZER_TYPE_CHOICES)
    config = serializers.JSONField(default=dict)

    class Meta:
        model = models.Analyzer
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        schema = get_config_schema().get(instance.type, {})
        config = data.get("config") or {}
        for field, meta in schema.items():
            if meta.get("sensitive") and field in config:
                config[field] = SENSITIVE_PLACEHOLDER
        data["config"] = config
        data["config_schema"] = {
            field: {"required": meta.get("required", False), "sensitive": meta.get("sensitive", False)}
            for field, meta in schema.items()
        }
        return data

    def validate(self, attrs):
        analyzer_type = attrs.get("type") or (self.instance.type if self.instance else None)
        config = attrs.get("config", {})

        schema = get_config_schema().get(analyzer_type, {})

        # If updating, merge with existing config to allow partial updates of non-sensitive fields
        if self.instance and self.instance.config:
            merged_config = dict(self.instance.config)
            for key, value in config.items():
                if value != SENSITIVE_PLACEHOLDER:
                    merged_config[key] = value
            config = merged_config
            attrs["config"] = config

        errors = {}
        for field, meta in schema.items():
            if meta.get("required") and not config.get(field):
                errors[field] = f"'{field}' is required for {analyzer_type} analyzer."
        if errors:
            raise serializers.ValidationError({"config": errors})

        return attrs


