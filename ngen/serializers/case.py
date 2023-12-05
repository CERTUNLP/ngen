from comment.models import Comment
from constance import config
from django.utils.translation import gettext
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
        read_only=True,
        view_name='artifact-detail'
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

    def validate_state(self, attrs):
        if self.instance is not None and self.instance.state != attrs and not self.instance.state.is_parent_of(attrs):
            raise ValidationError(
                {'state': gettext(
                    'It\'s not possible to change the state "%s" to "%s". The new possible states are %s') % (
                              self.instance.state, attrs, list(self.instance.state.children.all()))})
        return attrs

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        if self.instance:
            kwargs = extra_kwargs.get('state', {})
            action = self.context['view'].action
            if not kwargs.get('read_only', False):
                if action in ['update', 'partial_update']:
                    queryset = (self.instance.state.children.all() | models.State.objects.filter(
                        pk=self.instance.state.pk)).distinct()
                    kwargs['queryset'] = queryset
                else:
                    kwargs['queryset'] = models.State.get_initial().children.all()
                extra_kwargs['state'] = kwargs
        return extra_kwargs

    @staticmethod
    def allowed_fields():
        return config.ALLOWED_FIELDS_CASE.split(',')

    def get_comments(self, obj):
        comments_qs = Comment.objects.filter_parents_by_object(obj)
        return GenericRelationField(read_only=True).generic_detail_links(comments_qs, self.context.get('request'))


class CaseTemplateSerializer(AuditSerializerMixin):
    class Meta:
        model = models.CaseTemplate
        fields = '__all__'


class EvidenceSerializer(AuditSerializerMixin):
    related = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Evidence
        exclude = ['content_type', 'object_id']

    def get_related(self, obj):
        return GenericRelationField(read_only=True).generic_detail_link(obj.content_object, self.context.get('request'))
