import django_filters
from rest_framework import permissions, viewsets, filters

from ngen import models, serializers
from ngen.filters import StateFilter


class StateViewSet(viewsets.ModelViewSet):
    queryset = models.State.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ['name', 'description']
    filterset_class = StateFilter
    ordering_fields = ['id', 'created', 'modified',
                       'name', 'blocked', 'attended', 'solved', 'active']
    serializer_class = serializers.StateSerializer
    permission_classes = [permissions.IsAuthenticated]


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = models.Edge.objects.all()
    serializer_class = serializers.EdgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class StateMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.State.objects.all()
    serializer_class = serializers.StateMinifiedSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]
    