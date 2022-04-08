from constance import config
from django.db import IntegrityError
from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField

from ngen.models import Case, Network, Taxonomy, Feed, State, \
    User, NetworkEntity, Tlp, Priority, CaseTemplate, \
    Event, Report, IncidentStateChange, Edge, Contact, CaseEvidence, EventEvidence


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

        if action in ['update', 'partial_update', 'retrieve']:
            if self.instance.is_blocked():
                for field in self.instance._meta.fields:
                    if field.name not in self.allowed_fields():
                        kwargs = extra_kwargs.get(field.name, {})
                        kwargs['read_only'] = True
                        extra_kwargs[field.name] = kwargs

        return extra_kwargs

    def validate_parent(self, attrs):
        if self.instance == attrs:
            raise ValidationError({'parent': gettext('The parent must not be the same instance.')})
        return attrs

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            if self.instance.is_blocked():
                for attr in list(attrs):
                    if attr not in self.allowed_fields():
                        if config.ALLOWED_FIELDS_EXCEPTION:
                            raise ValidationError({attr: gettext('%s of blocked instances can\'t be modified') % attr})
                        attrs.pop(attr)
        return attrs

    @staticmethod
    def allowed_fields():
        raise NotImplementedError


class EventSerializer(MergeSerializerMixin, serializers.HyperlinkedModelSerializer, EvidenceSerializerMixin):
    evidence = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='eventevidence-detail'
    )
    children = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='event-detail'
    )

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
            if self.instance.is_merged() or self.instance.is_parent():
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

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['created_by']



class EventEvidenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventEvidence
        fields = '__all__'


class CaseSerializer(MergeSerializerMixin, serializers.HyperlinkedModelSerializer, EvidenceSerializerMixin):
    events = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='event-detail'
    )

    evidence = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='caseevidence-detail'
    )

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
                    self.instance.state.children.all() | State.objects.filter(pk=self.instance.state.pk)).distinct()
        else:
            kwargs['queryset'] = State.get_initial().children.all()
        extra_kwargs['state'] = kwargs
        return extra_kwargs

    @staticmethod
    def allowed_fields():
        return config.ALLOWED_FIELDS_CASE.split(',')

    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ['attend_date', 'solve_date', 'report_message_id', 'raw', 'created_by']


class CaseEvidenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CaseEvidence
        fields = '__all__'


class TaxonomySerializer(serializers.HyperlinkedModelSerializer):
    reports = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='report-detail'
    )

    class Meta:
        model = Taxonomy
        fields = '__all__'


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    problem = CharField(style={'base_template': 'textarea.html', 'rows': 10})
    derived_problem = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    verification = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    recommendations = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)
    more_information = CharField(style={'base_template': 'textarea.html', 'rows': 10}, allow_null=True)

    class Meta:
        model = Report
        fields = '__all__'


class FeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Feed
        fields = '__all__'


class StateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class IncidentStateChangeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentStateChange
        fields = '__all__'


class EdgeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Edge
        fields = '__all__'


class TlpSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tlp
        fields = '__all__'


class PrioritySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Priority
        fields = '__all__'


class CaseTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CaseTemplate
        fields = '__all__'


class NetworkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Network
        fields = '__all__'


class NetworkEntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NetworkEntity
        fields = '__all__'


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
