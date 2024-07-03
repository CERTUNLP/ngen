from constance import config
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ngen import models


class AuditSerializerMixin(serializers.HyperlinkedModelSerializer):
    history = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='logentry-detail'
    )


class EvidenceSerializerMixin(AuditSerializerMixin):

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


class ArtifactSerializerMixin(serializers.HyperlinkedModelSerializer):
    artifacts = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='artifact-detail',
        queryset=models.Artifact.objects.all(),
    )

    def update(self, instance, validated_data):
        """
        Update automatic artifacts relations deleting all and adding the new ones.
        Update manual artifacts relations deleting the ones that are not in the new list and adding the new ones.
        """
        artifacts = validated_data.pop('artifacts', [])
        super().update(instance, validated_data)
        ct = ContentType.objects.get_for_model(instance)
        # remove manual relations that are not in the new list and are not auto_created
        models.ArtifactRelation.objects.filter(
            object_id=instance.id,
            content_type=ct,
            auto_created=False
        ).exclude(
            artifact__in=artifacts
        ).delete()
        # find new manual relations
        new_artifacts = models.Artifact.objects.filter(
            pk__in=[artifact.pk for artifact in artifacts]
        ).exclude(
            artifact_relation__object_id=instance.id,
            artifact_relation__content_type=ct
        )
        # add new manual relations
        for artifact_obj in new_artifacts:
            models.ArtifactRelation.objects.get_or_create(
                artifact=artifact_obj,
                object_id=instance.id,
                content_type=ct,
                auto_created=False
            )
        return instance

    def create(self, validated_data):
        artifacts = validated_data.pop('artifacts', [])
        event = super().create(validated_data)
        # add new manual relations
        for artifact in artifacts:
            artifact_obj = models.Artifact.objects.get(pk=artifact.pk)
            models.ArtifactRelation.objects.create(artifact=artifact_obj, related=event, auto_created=False)
        return event


class MergeSerializerMixin:
    blocked = serializers.Field(source='blocked')

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        try:
            action = self.context['view'].action
        except KeyError:
            action = None
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
