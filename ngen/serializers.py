from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField

from ngen.models import Case, Network, Taxonomy, Feed, State, Behavior, \
    User, NetworkEntity, Tlp, Priority, CaseTemplate, \
    Event, Report, IncidentStateChange, Edge, Contact, CaseEvidence, EventEvidence


class EvidenceSerializerMixin(serializers.HyperlinkedModelSerializer):
    def save_evidence(self, event):
        request = self.context.get('request')
        files = request.FILES
        if files:
            try:
                for file in files.getlist('evidence'):
                    event.evidence.get_or_create(file=file)
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


class EventSerializer(EvidenceSerializerMixin):
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
    class Meta:
        model = Event
        fields = '__all__'


class EventEvidenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventEvidence
        fields = '__all__'


class CaseSerializer(EvidenceSerializerMixin):
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

    class Meta:
        model = Case
        fields = '__all__'


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


class BehaviorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Behavior
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
