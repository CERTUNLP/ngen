from rest_framework import serializers

from ngen.models import Incident, Network, IncidentType, IncidentFeed, IncidentState, StateBehavior, TaxonomyValue, \
    User, NetworkAdmin, NetworkEntity, TaxonomyPredicate, IncidentTlp, Host, IncidentPriority, IncidentImpact, \
    IncidentUrgency


class IncidentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Incident
        # fields = ['id', 'network', 'type', 'feed', 'state', 'reporter']
        fields = '__all__'
        # extra_kwargs = {
        #     'incidenttype': {'lookup_field': 'slug'},
        #     'incidentfeed': {'lookup_field': 'slug'},
        #     'incidentstate': {'lookup_field': 'slug'}
        # }


class IncidentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncidentType
        fields = '__all__'


class TaxonomyValueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonomyValue
        fields = '__all__'
        # extra_kwargs = {
        #     'taxonomypredicate': {'lookup_field': 'slug'}
        # }


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
        # extra_kwargs = {
        #     'statebehavior': {'lookup_field': 'slug'}
        # }


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


class NetworkSerializer(serializers.HyperlinkedModelSerializer):
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


class HostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
