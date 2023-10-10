from rest_framework import serializers
from rest_framework.fields import CharField

from ngen import models
from ngen.serializers.utils.mixins import NgenModelSerializer, EvidenceSerializerMixin


class AnnouncementSerializer(EvidenceSerializerMixin, NgenModelSerializer):
    body = CharField(style={'base_template': 'textarea.html', 'rows': 10})
    evidence = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='evidence-detail'
    )

    class Meta:
        model = models.Announcement
        fields = '__all__'


class CommentSerializer(NgenModelSerializer):
    class Meta:
        model = models.Comment
        exclude = ['content_type', 'object_id']
