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

        # print(events.all())

        domain_list = []
        cidr_list = []
        entity_events = []

        # networks = models.Network.objects.parents_of_many(events)
        # print(networks)
        # network_entities = models.NetworkEntity.objects.filter(networks__in=networks).prefetch_related('networks')
        #
        # for network_entity in network_entities:
        #     for network in network_entity.networks.all():
        #         domain = network.domain
        #         cidr = network.cidr
        #
        #         if domain is not None:
        #             domain_list.append(domain)
        #             entity_events += models.Event.objects.children_of_domain(domain)
        #
        #         if cidr is not None:
        #             cidr_list.append(cidr)
        #             entity_events += models.Event.objects.children_of_cidr(cidr)


        # for network in network_entity.networks.all():
        #     domain = network.domain
        #     cidr = network.cidr
        #
        #     if domain is not None:
        #         domain_list.append(domain)
        #         entity_events += models.Event.objects.children_of_domain(domain)
        #
        #     if cidr is not None:
        #         cidr_list.append(cidr)
        #         entity_events += models.Event.objects.children_of_cidr(cidr)

        # This uses exact match, but we may want entity_events to be a subtree search:
        # entity_events = events.filter(Q(domain__in=domain_list) | Q(cidr__in=cidr_list))

        #
        # networks = network_entity.networks.all()
        # print(networks)
        # print(network_entity)
        #
        # for event in events.all():
        #     # print(event)
        #     for network in networks:
        #         # print(network)
        #         domain = network.domain
        #         cidr = network.cidr
        #         # print(domain, cidr, event.domain, event.cidr)
        #
        #         if domain and event.domain:
        #             if event.domain.endswith(domain):
        #                 entity_events.append(event)
        #         elif cidr and event.cidr:
        #             if ipaddress.ip_network(event.cidr) in ipaddress.ip_network(cidr):
        #                 entity_events.append(event)

        entity_events = events.filter(network__in=network_entity.networks.all())

        return EventSerializerReduced(
            entity_events, many=True, context=self.context
        ).data
        # print(entity_events)
        # return len(entity_events)


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
