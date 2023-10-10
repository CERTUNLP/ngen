import django_filters
from rest_framework import permissions, filters, viewsets

from ngen import models, serializers
from ngen.filters import NetworkFilter


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = models.Network.objects.all()
    serializer_class = serializers.NetworkSerializer
    filter_backends = [filters.SearchFilter,
                       django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter
    ]
    search_fields = ['cidr', 'type', 'domain']
    filterset_class = NetworkFilter
    ordering_fields = ['id', 'created', 'modified', 'cidr', 'domain', 'type']
    permission_classes = [permissions.IsAuthenticated]


class NetworkEntityViewSet(viewsets.ModelViewSet):
    queryset = models.Network.objects.all()
    serializer_class = serializers.NetworkSerializer
    filter_backends = [filters.SearchFilter,
                       django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter
    ]
    search_fields = ['cidr', 'type', 'domain']
    filterset_class = NetworkFilter
    ordering_fields = ['id', 'created', 'modified', 'cidr', 'domain', 'type']
    permission_classes = [permissions.IsAuthenticated]


class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
