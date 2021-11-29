from rest_framework import serializers

from ngen.models import Incident, Network, IncidentType, IncidentFeed, IncidentState, StateBehavior, TaxonomyValue, \
    User, NetworkAdmin, NetworkEntity, TaxonomyPredicate, IncidentTlp, IncidentPriority, IncidentImpact, \
    IncidentUrgency, IncidentDecision, IncidentDetected, IncidentReport, IncidentStateChange, StateEdge, Contact, \
    ContactCase


class IncidentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Incident
        # fields = ['id', 'network', 'type', 'feed', 'state', 'reporter']
        fields = '__all__'


class IncidentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentType
        fields = '__all__'


class IncidentReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentReport
        fields = '__all__'


class TaxonomyValueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonomyValue
        fields = '__all__'


class TaxonomyPredicateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonomyPredicate
        fields = '__all__'


class IncidentFeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentFeed
        fields = '__all__'


class IncidentStateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentState
        fields = '__all__'


class IncidentStateChangeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentStateChange
        fields = '__all__'


class StateEdgeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StateEdge
        fields = '__all__'


class StateBehaviorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StateBehavior
        fields = '__all__'


class IncidentTlpSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentTlp
        fields = '__all__'


class IncidentPrioritySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentPriority
        fields = '__all__'


class IncidentUrgencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentUrgency
        fields = '__all__'


class IncidentImpactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentImpact
        fields = '__all__'


class IncidentDecisionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentDecision
        fields = '__all__'


class IncidentDetectedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentDetected
        fields = '__all__'


class NetworkSerializer(serializers.HyperlinkedModelSerializer):
    # host_set = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='host-detail'
    # )

    class Meta:
        model = Network
        fields = '__all__'


class NetworkAdminSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NetworkAdmin
        fields = '__all__'


class NetworkEntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NetworkEntity
        fields = '__all__'


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class ContactCaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContactCase
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
