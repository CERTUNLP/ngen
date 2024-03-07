from comment.models import Comment
from constance import config
from django.utils.translation import gettext
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ngen import models
from ngen.serializers.common.fields import GenericRelationField, SlugOrHyperlinkedRelatedField
from ngen.serializers.common.mixins import AuditSerializerMixin, MergeSerializerMixin, EvidenceSerializerMixin


class EventSerializer(MergeSerializerMixin, EvidenceSerializerMixin, AuditSerializerMixin):
    feed = SlugOrHyperlinkedRelatedField(
        slug_field='slug',
        queryset=models.Feed.objects.all(),
        view_name='feed-detail'
    )
    tlp = SlugOrHyperlinkedRelatedField(
        slug_field='slug',
        queryset=models.Tlp.objects.all(),
        view_name='tlp-detail'
    )
    priority = SlugOrHyperlinkedRelatedField(
        slug_field='slug',
        queryset=models.Priority.objects.all(),
        view_name='priority-detail'
    )
    taxonomy = SlugOrHyperlinkedRelatedField(
        slug_field='slug',
        queryset=models.Taxonomy.objects.all(),
        view_name='taxonomy-detail'
    )
    evidence = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='evidence-detail'
    )
    children = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='event-detail'
    )
    todos = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='todo-detail'
    )
    artifacts = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='artifact-detail',
        queryset=models.Artifact.objects.all()
    )
    reporter = serializers.HyperlinkedRelatedField(
        default=serializers.CreateOnlyDefault(
            serializers.CurrentUserDefault()),
        queryset=models.User.objects.all(),
        view_name='user-detail'
    )
    comments = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = '__all__'

    def get_comments(self, obj):
        comments_qs = Comment.objects.filter_parents_by_object(obj)
        return GenericRelationField(read_only=True).generic_detail_links(comments_qs, self.context.get('request'))

    @staticmethod
    def allowed_fields():
        return config.ALLOWED_FIELDS_EVENT.split(',')

    @staticmethod
    def not_allowed_fields():
        return ['taxonomy', 'feed', 'network']

    def update(self, instance, validated_data):
        artifacts = validated_data.pop('artifacts', [])
        ct = ContentType.objects.get_for_model(instance)
        # remove relations that are not in the new list
        models.ArtifactRelation.objects.filter(
            object_id=instance.id,
            content_type=ct
        ).exclude(
            artifact__in=artifacts
        ).delete()
        for artifact in artifacts:
            artifact_obj = models.Artifact.objects.get(pk=artifact.pk)
            models.ArtifactRelation.objects.get_or_create(
                artifact=artifact_obj,
                object_id=instance.id,
                content_type=ct)
        return instance

    def create(self, validated_data):
        artifacts = validated_data.pop('artifacts', [])
        event = super().create(validated_data)
        for artifact in artifacts:
            artifact_obj = models.Artifact.objects.get(pk=artifact.pk)
            models.ArtifactRelation.objects.create(artifact=artifact_obj, related=event)
        return event

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        action = self.context['view'].action
        if action in ['update', 'partial_update', 'retrieve']:
            if self.instance and self.instance.is_parent():
                for field in self.instance._meta.fields:
                    if field.name in self.not_allowed_fields():
                        kwargs = extra_kwargs.get(field.name, {})
                        kwargs['read_only'] = True
                        extra_kwargs[field.name] = kwargs

        return extra_kwargs

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if self.instance:
            if self.instance.merged or self.instance.is_parent():
                for attr in list(attrs):
                    if attr in self.not_allowed_fields():
                        if config.ALLOWED_FIELDS_EXCEPTION:
                            raise ValidationError(
                                {attr: gettext('%s of merged events can\'t be modified') % self.not_allowed_fields()})
                        attrs.pop(attr)
        return attrs


class EventSerializerReduced(MergeSerializerMixin, EvidenceSerializerMixin, AuditSerializerMixin):

    @staticmethod
    def allowed_fields():
        return config.ALLOWED_FIELDS_EVENT.split(',')

    class Meta:
        model = models.Event
        fields = [
            "url",
            "uuid",
            "created",
            "modified",
            "feed",
            "tlp",
            "priority",
            "taxonomy",
            "cidr",
            "domain",
            "address_value",
            "date",
            "reporter",
        ]


class CaseSerializer(MergeSerializerMixin, EvidenceSerializerMixin, AuditSerializerMixin):
    events = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=models.Event.objects.all(),
        view_name='event-detail'
    )
    children = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='case-detail'
    )
    evidence = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField()
    user_creator = serializers.HyperlinkedRelatedField(
        default=serializers.CreateOnlyDefault(
            serializers.CurrentUserDefault()),
        queryset=models.User.objects.all(),
        view_name='user-detail'
    )
    state = SlugOrHyperlinkedRelatedField(
        slug_field='slug',
        queryset=models.State.objects.all(),
        view_name='state-detail'
    )
    template_creator = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='casetemplate-detail'
    )

    class Meta:
        model = models.Case
        fields = '__all__'
        read_only_fields = ['attend_date', 'solve_date',
                            'report_message_id', 'raw', 'created_by', 'notification_count']

    def get_evidence(self, obj):
        return GenericRelationField(read_only=True).generic_detail_links(obj.evidence_all, self.context.get('request'))

    @staticmethod
    def allowed_fields():
        return config.ALLOWED_FIELDS_CASE.split(',')

    def get_comments(self, obj):
        comments_qs = Comment.objects.filter_parents_by_object(obj)
        return GenericRelationField(read_only=True).generic_detail_links(comments_qs, self.context.get('request'))


class CaseSerializerReduced(MergeSerializerMixin, EvidenceSerializerMixin, AuditSerializerMixin):

    @staticmethod
    def allowed_fields():
        return config.ALLOWED_FIELDS_CASE.split(',')

    class Meta:
        model = models.Case
        fields = [
            "url",
            "uuid",
            "created",
            "modified",
            "tlp",
            "priority",
            "date",
            "attend_date",
            "solve_date",
            "lifecycle",
            "state",
            "assigned",
        ]


class CaseSerializerReducedWithEventsCount(CaseSerializerReduced):
    events_count = serializers.SerializerMethodField()

    class Meta(CaseSerializerReduced.Meta):
        fields = CaseSerializerReduced.Meta.fields + ["events_count"]

    def get_events_count(self, obj):
        return obj.events.count()


class CaseTemplateSerializer(AuditSerializerMixin):
    matching_events_without_case = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.CaseTemplate
        fields = '__all__'

    def get_matching_events_without_case(self, obj):
        return obj.matching_events_without_case().count()


class EvidenceSerializer(AuditSerializerMixin):
    related = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Evidence
        exclude = ['content_type', 'object_id']

    def get_related(self, obj):
        return GenericRelationField(read_only=True).generic_detail_link(obj.content_object, self.context.get('request'))


class CaseMinifiedSerializer(AuditSerializerMixin):
    class Meta:
        model = models.Case
        fields = ['url', 'uuid', 'name']
