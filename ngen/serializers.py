from constance import config
from django.db import IntegrityError
from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField

from ngen import models
from ngen.models import utils


class GenericRelationField(serializers.RelatedField):
    def to_internal_value(self, data):
        pass

    def to_representation(self, related_list):
        return self.generic_detail_links(related_list)

    def generic_detail_links(self, related_list, request=None):
        links = []
        for related in related_list:
            links.append(self.generic_detail_link(related, request))
        return links

    def generic_detail_link(self, related, request=None):
        view_name = related.__class__.__name__.lower() + '-detail'
        serializer = serializers.HyperlinkedIdentityField(view_name=view_name)
        return serializer.get_url(obj=related, view_name=view_name,
                                  request=self.context.get('request', request),
                                  format=None)


class EvidenceSerializerMixin:
    def save_evidence(self, instance):
        request = self.context.get('request')
        files = request.FILES
        if files:
            try:
                for file in files.getlist('evidence'):
                    instance.add_evidence(file)
            except IntegrityError as e:
                raise ValidationError({'evidence': e})

    def update(self, instance, validated_data):
        event = super().update(instance, validated_data)
        self.save_evidence(event)
        return event

    def create(self, validated_data):
        event = super().create(validated_data)
        self.save_evidence(event)
        return event


class MergeSerializerMixin:
    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        action = self.context['view'].action
        allowed_fields = self.allowed_fields()
        if action in ['update', 'partial_update', 'retrieve']:
            if self.instance and self.instance.is_blocked():
                for field in self.instance._meta.fields:
                    if field.name not in allowed_fields:
                        kwargs = extra_kwargs.get(field.name, {})
                        kwargs['read_only'] = True
                        extra_kwargs[field.name] = kwargs

        return extra_kwargs

    def validate_parent(self, parent: 'utils.NgenMergeableModel'):
        if parent and not parent.is_mergeable_with(self.instance):
            raise ValidationError({'parent': gettext('The parent must not be the same instance.')})
        return parent

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance and self.instance.is_blocked():
            allowed_fields = self.allowed_fields()
            for attr in list(attrs):
                if attr not in allowed_fields:
                    if config.ALLOWED_FIELDS_EXCEPTION:
                        raise ValidationError({attr: gettext('%s of blocked instances can\'t be modified') % attr})
                    attrs.pop(attr)
        return attrs

    @staticmethod
    def allowed_fields():
        raise NotImplementedError


class EventSerializer(MergeSerializerMixin, EvidenceSerializerMixin, serializers.HyperlinkedModelSerializer):
    evidence_all = GenericRelationField(read_only=True)
    children = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='event-detail'
    )
    todos = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='todotask-detail'
    )
    artifacts = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='artifact-detail'
    )

    class Meta:
        model = models.Event
        fields = '__all__'

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
            if self.instance and (self.instance.is_merged() or self.instance.is_parent()):
                for field in self.instance._meta.fields:
                    if field.name in self.not_allowed_fields():
                        kwargs = extra_kwargs.get(field.name, {})
                        kwargs['read_only'] = True
                        extra_kwargs[field.name] = kwargs

        return extra_kwargs

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            if self.instance.is_merged() or self.instance.is_parent():
                for attr in list(attrs):
                    if attr in self.not_allowed_fields():
                        if config.ALLOWED_FIELDS_EXCEPTION:
                            raise ValidationError(
                                {attr: gettext('%s of merged events can\'t be modified') % self.not_allowed_fields()})
                        attrs.pop(attr)
        return attrs


class CaseSerializer(MergeSerializerMixin, EvidenceSerializerMixin, serializers.HyperlinkedModelSerializer):
    events = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='event-detail'
    )
    children = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='case-detail'
    )
    evidence = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Case
        fields = '__all__'
        read_only_fields = ['attend_date', 'solve_date', 'report_message_id', 'raw', 'created_by']

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
        kwargs = extra_kwargs.get('state', {})
        action = self.context['view'].action

        if action in ['update', 'partial_update']:
            kwargs['queryset'] = (
                    self.instance.state.children.all() | models.State.objects.filter(
                pk=self.instance.state.pk)).distinct()
        else:
            kwargs['queryset'] = models.State.get_initial().children.all()
        extra_kwargs['state'] = kwargs
        return extra_kwargs

    @staticmethod
    def allowed_fields():
        return config.ALLOWED_FIELDS_CASE.split(',')


class EvidenceSerializer(serializers.HyperlinkedModelSerializer):
    related = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Evidence
        exclude = ['content_type', 'object_id']

    def get_related(self, obj):
        return GenericRelationField(read_only=True).generic_detail_link(obj.content_object, self.context.get('request'))


class TaxonomySerializer(serializers.HyperlinkedModelSerializer):
    reports = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='report-detail'
    )

    class Meta:
        model = models.Taxonomy
        fields = '__all__'


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    problem = CharField(style={'base_template': 'textarea.html', 'rows': 10})
    derived_problem = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    verification = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    recommendations = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    more_information = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)

    class Meta:
        model = models.Report
        fields = '__all__'


class FeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Feed
        fields = '__all__'


class StateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.State
        fields = '__all__'


class EdgeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Edge
        fields = '__all__'


class TlpSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Tlp
        fields = '__all__'


class PrioritySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Priority
        fields = '__all__'

    def validate(self, attrs):
        if self.instance is not None and not (attrs['solve_time'] > attrs['attend_deadline']):
            raise ValidationError({'solve_time': gettext('The solve time must be greater than attend deadline')})
        return attrs


class CaseTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CaseTemplate
        fields = '__all__'


class NetworkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Network
        fields = '__all__'


class NetworkEntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.NetworkEntity
        fields = '__all__'


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Contact
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.User
        exclude = ['user_permissions', 'password', 'groups']


class PlaybookSerializer(serializers.HyperlinkedModelSerializer):
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='task-detail'
    )

    class Meta:
        model = models.Playbook
        fields = '__all__'


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Task
        fields = '__all__'


class TodoTaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TodoTask
        fields = '__all__'
        read_only_fields = ['completed_date', 'task', 'event']


class ArtifactSerializer(serializers.HyperlinkedModelSerializer):
    related = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Artifact
        fields = '__all__'

    def get_related(self, obj):
        return GenericRelationField(read_only=True).generic_detail_links(obj.related, self.context.get('request'))
