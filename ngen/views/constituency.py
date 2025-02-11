import django_filters
from django.db.models import Count
from rest_framework import filters, viewsets, mixins

from ngen import models, serializers
from ngen.filters import NetworkFilter, ContactFilter, NetworkEntityFilter
from ngen.permissions import (
    CustomApiViewPermission,
    CustomMethodApiViewPermission,
    CustomModelPermissions,
)


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = models.Network.objects.annotate(
        contact_count=Count("contacts"), children_count=Count("children")
    )
    serializer_class = serializers.NetworkSerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = [
        "cidr",
        "type",
        "domain",
        "contacts__username",
        "network_entity__name",
    ]
    filterset_class = NetworkFilter
    ordering_fields = [
        "id",
        "created",
        "modified",
        "cidr",
        "domain",
        "type",
        "active",
        "address_value",
        "network_entity",
        "network_entity__name",
        "contact_count",
        "contacts__username",
        "children_count",
    ]
    permission_classes = [CustomModelPermissions]


class NetworkAdminNetworkViewSet(NetworkViewSet):
    serializer_class = serializers.NetworkAdminNetworkSerializer
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["ngen.view_network_network_admin"],
        "HEAD": ["ngen.view_network_network_admin"],
        "POST": ["ngen.add_network_network_admin"],
        "PUT": ["ngen.change_network_network_admin"],
        "PATCH": ["ngen.change_network_network_admin"],
        "DELETE": ["ngen.delete_network_network_admin"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(contacts__user=user).distinct()


class NetworkEntityViewSet(viewsets.ModelViewSet):
    queryset = models.NetworkEntity.objects.annotate(
        networks_count=Count("networks")
    ).order_by("id")
    serializer_class = serializers.NetworkEntitySerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "slug"]
    filterset_class = NetworkEntityFilter
    ordering_fields = ["id", "created", "modified", "name", "slug", "networks_count"]
    permission_classes = [CustomModelPermissions]


class NetworkAdminNetworkEntityViewSet(NetworkEntityViewSet):
    serializer_class = serializers.NetworkAdminNetworkEntitySerializer
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["ngen.view_networkentity_network_admin"],
        "HEAD": ["ngen.view_networkentity_network_admin"],
        "POST": ["ngen.add_networkentity_network_admin"],
        "PUT": ["ngen.change_networkentity_network_admin"],
        "PATCH": ["ngen.change_networkentity_network_admin"],
        "DELETE": ["ngen.delete_networkentity_network_admin"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(networks__contacts__user=user).distinct()


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
    permission_classes = [CustomModelPermissions]


class NetworkAdminContactViewSet(ContactViewSet):
    serializer_class = serializers.NetworkAdminContactSerializer
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["ngen.view_contact_network_admin"],
        "HEAD": ["ngen.view_contact_network_admin"],
        "POST": ["ngen.add_contact_network_admin"],
        "PUT": ["ngen.change_contact_network_admin"],
        "PATCH": ["ngen.change_contact_network_admin"],
        "DELETE": ["ngen.delete_contact_network_admin"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # user is contact.user or networks are in networks__contacts for user
        return queryset.filter(
            models.Q(user=user) | models.Q(networks__contacts__user=user)
        ).distinct()


class EntityMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.NetworkEntity.objects.all()
    serializer_class = serializers.EntityMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_entity"]


class ContactMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_contact"]
