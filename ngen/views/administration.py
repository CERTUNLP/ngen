import django_filters
from rest_framework import permissions, filters, viewsets

from ngen import models, serializers
from ngen.filters import FeedFilter, PriorityFilter, TlpFilter


class FeedViewSet(viewsets.ModelViewSet):
    queryset = models.Feed.objects.all().order_by('id')
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ['name', 'description']
    filterset_class = FeedFilter
    ordering_fields = ['id', 'created', 'modified', 'name', 'slug']
    serializer_class = serializers.FeedSerializer
    permission_classes = [permissions.IsAuthenticated]


class PriorityViewSet(viewsets.ModelViewSet):
    queryset = models.Priority.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ['name']
    filterset_class = PriorityFilter
    ordering_fields = ['id', 'created', 'modified', 'name', 'slug', 'severity']
    serializer_class = serializers.PrioritySerializer
    permission_classes = [permissions.IsAuthenticated]


class TlpViewSet(viewsets.ModelViewSet):
    queryset = models.Tlp.objects.all().order_by('id')
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ['name']
    filterset_class = TlpFilter
    ordering_fields = ['id', 'created', 'modified', 'name', 'slug', 'code']
    serializer_class = serializers.TlpSerializer
    permission_classes = [permissions.IsAuthenticated]
