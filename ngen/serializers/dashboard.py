from django.db.models import Q
from ngen.models.constituency import NetworkEntity
from rest_framework import serializers
from ngen.serializers import (
    EventSerializerReduced,
    CaseSerializerReduced,
    NetworkEntitySerializerReduced,
)


class FeedsInEventsSerializer(serializers.Serializer):
    """
    Serializer for the feeds and the amount of events they are involved in.
    """

    feed_name = serializers.CharField()
    event_count = serializers.IntegerField()


class FeedDashboardSerializer(serializers.Serializer):
    """
    Serializer for the feed data, including the total amount of events.
    """

    total_events_count = serializers.IntegerField()
    feeds_in_events = FeedsInEventsSerializer(many=True)


class NetworkEntityDashboardSerializer(NetworkEntitySerializerReduced):
    """
    Serializer for Network Entities, including the events related with their networks.
    """

    events = serializers.SerializerMethodField()

    def get_events(self, network_entity):
        """
        Get the events related with the networks of the Network Entity.
        The association is made by network domain or cidr.
        """

        events = self.context.get("events")

        domain_list = [
            domain
            for domain in network_entity.networks.values_list("domain", flat=True)
            if domain is not None
        ]

        cidr_list = [
            cidr
            for cidr in network_entity.networks.values_list("cidr", flat=True)
            if cidr is not None
        ]

        entity_events = events.filter(Q(domain__in=domain_list) | Q(cidr__in=cidr_list))

        return EventSerializerReduced(
            entity_events, many=True, context=self.context
        ).data


class DashboardSerializer(serializers.Serializer):
    """
    Serializer for the dashboard view.
    """

    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    cases = CaseSerializerReduced(many=True)
    events = EventSerializerReduced(many=True)
    feeds = FeedDashboardSerializer()

    def to_representation(self, instance):
        """
        Add the network_entities field to the representation.
        """
        network_entity_serializer = NetworkEntityDashboardSerializer(
            instance=self.context["network_entities"], many=True, context=self.context
        )

        representation = super().to_representation(instance)
        representation["network_entities"] = network_entity_serializer.data

        return representation
