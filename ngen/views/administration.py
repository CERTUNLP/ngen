import django_filters
from rest_framework import permissions, filters, viewsets
from django.db.models import Count

from ngen import models, serializers
from ngen.filters import FeedFilter, PriorityFilter, TlpFilter


class FeedViewSet(viewsets.ModelViewSet):
    queryset = models.Feed.objects.annotate(events_count=Count('event')).order_by('id')
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ['name', 'description']
    filterset_class = FeedFilter
    ordering_fields = ['id', 'created', 'modified', 'name', 'slug', 'events_count']
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
    ordering_fields = ['id', 'created', 'modified', 'name', 'slug', 'severity', 'attend_time', 'solve_time']
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


class FeedMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.Feed.objects.all()
    serializer_class = serializers.FeedMinifiedSerializer
    pagination_class = None


class TlpMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.Tlp.objects.all()
    serializer_class = serializers.TlpMinifiedSerializer
    pagination_class = None


class PriorityMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.Priority.objects.all()
    serializer_class = serializers.PriorityMinifiedSerializer
    pagination_class = None
