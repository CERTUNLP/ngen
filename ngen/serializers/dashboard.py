from rest_framework import serializers

from ngen.serializers import (
    EventSerializerReduced,
    CaseSerializerReducedWithEventsCount,
    NetworkEntitySerializerReduced,
)


class DashboardSerializer(serializers.Serializer):
    """
    Parent serializer for the dashboard view. It includes the date_from and date_to.
    """

    date_from = serializers.DateTimeField()
    date_to = serializers.DateTimeField()


class EventDashboardSerializer(DashboardSerializer):
    """
    Serializer for the events.
    """

    events = EventSerializerReduced(many=True)


class CaseDashboardSerializer(DashboardSerializer):
    """
    Serializer for the cases.
    """

    cases = CaseSerializerReducedWithEventsCount(many=True)


class FeedsInEventsSerializer(serializers.Serializer):
    """
    Serializer for the feeds and the amount of events they are involved in.
    """

    feed_name = serializers.CharField()
    events_count = serializers.IntegerField()


class FeedDashboardSerializer(DashboardSerializer):
    """
    Serializer for the feed data, including the total amount of events.
    """

    total_events_count = serializers.IntegerField()
    feeds_in_events = FeedsInEventsSerializer(many=True)


class NetworkEntitiesWithEventsSerializer(NetworkEntitySerializerReduced):
    events = serializers.SerializerMethodField()

    def get_events(self, network_entity):
        """
        Get the events related with the networks of the Network Entity.
        The association is made by network domain or cidr.
        """

        events = self.context.get("events")
        entity_events = []
        entity_events = events.filter(network__in=network_entity.networks.all())

        return EventSerializerReduced(
            entity_events, many=True, context=self.context
        ).data


class NetworkEntityDashboardSerializer(DashboardSerializer):
    """
    Serializer for Network Entities, including the events related with their networks.
    """

    def to_representation(self, instance):
        """
        Overwrite to_representation to add the network entities with their related events.
        """
        representation = super().to_representation(instance)

        representation["network_entities"] = NetworkEntitiesWithEventsSerializer(
            instance["network_entities"], many=True, context=self.context
        ).data

        return representation
