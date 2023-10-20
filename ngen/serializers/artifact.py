from generic_relations.relations import GenericRelatedField
from rest_framework import serializers

from ngen import models
from ngen.serializers.common.fields import GenericRelationField
from ngen.serializers.common.mixins import AuditSerializerMixin


class ArtifactEnrichmentSerializer(AuditSerializerMixin):
    class Meta:
        model = models.ArtifactEnrichment
        fields = '__all__'


class ArtifactSerializer(AuditSerializerMixin):
    related = serializers.SerializerMethodField(read_only=True)
    enrichments = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='artifactenrichment-detail'
    )

    class Meta:
        model = models.Artifact
        fields = '__all__'

    def get_related(self, obj):
        return GenericRelationField(read_only=True).generic_detail_links(obj.related, self.context.get('request'))


class ArtifactRelationSerializer(AuditSerializerMixin):
    content_type_description = serializers.SerializerMethodField()
    content_type = serializers.HyperlinkedRelatedField(
        view_name='contenttype-detail',
        read_only=True
    )
    related = GenericRelatedField({
        models.Event: serializers.HyperlinkedRelatedField(
            queryset=models.Event.objects.all(),
            view_name='event-detail',
        ),
        models.Case: serializers.HyperlinkedRelatedField(
            queryset=models.Case.objects.all(),
            view_name='case-detail',
        ),
    })

    class Meta:
        model = models.ArtifactRelation
        fields = ('url', 'artifact', 'related', 'content_type', 'content_type_description', 'object_id')
        read_only_fields = ('content_type', 'object_id', 'content_type_description')

    def get_content_type_description(self, obj):
        return str(obj.content_type)
