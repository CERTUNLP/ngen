from auditlog.models import LogEntry
from constance import config, settings
from django.conf import settings as project_settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import ngen.models.common.parsing
from ngen.serializers.common.fields import GenericRelationField, ConstanceValueField
from ngen.serializers.common.mixins import AuditSerializerMixin
from ngen.utils import get_settings


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'


class AuditSerializer(AuditSerializerMixin):
    related = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LogEntry
        fields = '__all__'

    def get_related(self, obj):
        try:
            new_obj = obj.content_type.get_object_for_this_type(
                pk=obj.object_id)
            return GenericRelationField(read_only=True).generic_detail_link(new_obj, self.context.get('request'))
        except ObjectDoesNotExist:
            return None


class ConstanceSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    key = serializers.CharField()
    default = serializers.SerializerMethodField()
    help_text = serializers.SerializerMethodField()
    value_type = serializers.SerializerMethodField()
    value = ConstanceValueField()
    settings = None

    def get_settings(self):
        if not self.settings:
            self.settings = get_settings()
        return self.settings

    def get_url(self, obj):
        return f"{self.context.get('request').build_absolute_uri().split('?')[0]}{obj['key']}/"

    def get_default(self, obj):
        value = next((item for item in self.get_settings()
                      if item["key"] == obj['key']), None)
        return value['default'] if value else None

    def get_help_text(self, obj):
        value = next((item for item in self.get_settings()
                      if item["key"] == obj['key']), None)
        return value['help_text'] if value else None

    def get_value_type(self, obj):
        value = next((item for item in self.get_settings()
                      if item["key"] == obj['key']), None)
        return value['value_type'] if value else None

    def is_valid(self, raise_exception=False):
        super().is_valid()
        if not 'value' in self.validated_data:
            raise ValidationError('No value provided')
        return True

    def create(self, validated_data):
        key = validated_data.get('key')
        value = validated_data.get('value')

        try:
            value_type = type(settings.CONFIG.get(key)[0])
            if value_type == bool:
                value = str(value).lower() in project_settings.VALUES_TRUE
            else:
                value = value_type(value)
            setattr(config, key, '' if value is None else value)
        except AttributeError as e:
            raise serializers.ValidationError(f'Invalid key. {e}')
        except ValidationError as e:
            raise serializers.ValidationError(f'Invalid value. {e}')
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return validated_data

    def update(self, instance, validated_data):
        return self.create(validated_data)


class StringIdentifierSerializer(serializers.Serializer):
    input_string = serializers.CharField(required=True)

    class Meta:
        model = ngen.models.common.parsing.StringIdentifier
        fields = '__all__'
        read_only_fields = ['input_type',
                            'address_string', 'address_type', 'all_types']

    def create(self, validated_data):
        rf = ['parsed_obj']
        data = {k: v for k, v in ngen.models.common.parsing.StringIdentifier(
            **validated_data).__dict__.items() if k not in rf}
        return data

    def list(self):
        return {'all_types': ngen.models.common.parsing.StringType._member_names_,
                'all_network_types': ngen.models.common.parsing.StringIdentifier.all_network_types(),
                'all_artifact_types': ngen.models.common.parsing.StringIdentifier.all_artifact_types()}
