import django_filters
from rest_framework import permissions, filters, viewsets
from django.db.models import Count
from ngen import models, serializers
from ngen.filters import NetworkFilter, ContactFilter, NetworkEntityFilter


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = models.Network.objects.all()
    serializer_class = serializers.NetworkSerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["cidr", "type", "domain"]
    filterset_class = NetworkFilter
    ordering_fields = ["id", "created", "modified", "cidr", "domain", "type", "address_value", "network_entity",
                       "network_entity__name"]
    permission_classes = [permissions.IsAuthenticated]


class NetworkEntityViewSet(viewsets.ModelViewSet):
    queryset = models.NetworkEntity.objects.annotate(networks_count=Count('networks')).order_by("id")
    serializer_class = serializers.NetworkEntitySerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "slug"]
    filterset_class = NetworkEntityFilter
    ordering_fields = ["id", "created", "modified", "name", "slug", "networks_count"]
    permission_classes = [permissions.IsAuthenticated]


class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "username", "role"]
    filterset_class = ContactFilter
    ordering_fields = [
        "id",
        "created",
        "modified",
        "name",
        "username",
        "role",
        "priority",
    ]
    permission_classes = [permissions.IsAuthenticated]


class EntityMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.NetworkEntity.objects.all()
    serializer_class = serializers.EntityMinifiedSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]


class ContactMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactMinifiedSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]
