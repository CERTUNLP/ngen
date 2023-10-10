from rest_framework import serializers


class NgenModelSerializer(serializers.HyperlinkedModelSerializer):
    history = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='logentry-detail'
    )


class EvidenceSerializerMixin(NgenModelSerializer):

    def update(self, instance, validated_data):
        files = self.context.get('request').FILES
        if files:
            validated_data['files'] = files.getlist('evidence')
        event = super().update(instance, validated_data)
        return event

    def create(self, validated_data):
        files = self.context.get('request').FILES
        if files:
            validated_data['files'] = files.getlist('evidence')
        event = super().create(validated_data)
        return event


class MergeSerializerMixin:
    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        action = self.context['view'].action
        if action in ['update', 'partial_update', 'retrieve'] and self.instance and not self.instance.mergeable:
            if self.instance.blocked:
                allowed_fields = self.allowed_fields()
            elif self.instance.merged:
                allowed_fields = []
            for field in self.instance._meta.fields:
                if field.name not in allowed_fields:
                    kwargs = extra_kwargs.get(field.name, {})
                    kwargs['read_only'] = True
                    if field.is_relation:
                        kwargs['queryset'] = None
                    extra_kwargs[field.name] = kwargs

        return extra_kwargs

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance and self.instance.merged:
            raise ValidationError(
                gettext('Merged instances can\'t be modified'))
        if self.instance and self.instance.blocked:
            allowed_fields = self.allowed_fields()
            for attr in list(attrs):
                if attr not in allowed_fields:
                    if config.ALLOWED_FIELDS_EXCEPTION:
                        raise ValidationError(
                            {attr: gettext('%s of blocked instances can\'t be modified') % attr})
                    attrs.pop(attr)
        return attrs

    @staticmethod
    def allowed_fields():
        raise NotImplementedError
