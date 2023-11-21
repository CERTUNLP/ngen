import django_filters
from rest_framework import permissions, filters, viewsets

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
    ordering_fields = ["id", "created", "modified", "cidr", "domain", "type"]
    permission_classes = [permissions.IsAuthenticated]


class NetworkEntityViewSet(viewsets.ModelViewSet):
    queryset = models.NetworkEntity.objects.all().order_by("id")
    serializer_class = serializers.NetworkEntitySerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "slug"]
    filterset_class = NetworkEntityFilter
    ordering_fields = ["id", "created", "modified", "name", "slug"]
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
