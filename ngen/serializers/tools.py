import jwt
from auditlog.models import LogEntry
from constance import config
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from ngen import models
from ngen.utils import get_settings
from ngen.serializers.utils.fields import GenericRelationField, ConstanceValueField
from ngen.serializers.utils.mixins import NgenModelSerializer


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'


class AuditSerializer(NgenModelSerializer):
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
            setattr(config, key, '' if value is None else value)
        except AttributeError:
            raise serializers.ValidationError('Invalid key')
        except ValidationError:
            raise serializers.ValidationError('Invalid value')
        return validated_data

    def update(self, instance, validated_data):
        return self.create(validated_data)


class StringIdentifierSerializer(serializers.Serializer):
    input_string = serializers.CharField(required=True)

    class Meta:
        model = models.StringIdentifier
        fields = '__all__'
        read_only_fields = ['input_type',
                            'address_string', 'address_type', 'all_types']

    def create(self, validated_data):
        rf = ['parsed_obj']
        data = {k: v for k, v in models.StringIdentifier(
            **validated_data).__dict__.items() if k not in rf}
        return data

    def list(self):
        return {'all_types': models.StringType._member_names_,
                'all_network_types': models.StringIdentifier.all_network_types(),
                'all_artifact_types': models.StringIdentifier.all_artifact_types()}
