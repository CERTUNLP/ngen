import django_filters
from rest_framework import permissions, filters, viewsets

from ngen import models, serializers, backends
from ngen.filters import EventFilter, CaseFilter, CaseTemplateFilter


class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = models.Evidence.objects.all()
    serializer_class = serializers.EvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Event.objects.all()
    filter_backends = [backends.MergedModelFilterBackend, filters.SearchFilter,
                       django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter]
    search_fields = ['taxonomy__name', 'feed__name',
                     'address_value', 'cidr', 'domain']
    filterset_class = EventFilter
    ordering_fields = ['id', 'date', 'priority', 'reporter']
    serializer_class = serializers.EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseViewSet(viewsets.ModelViewSet):
    queryset = models.Case.objects.all()
    filter_backends = [
        backends.MergedModelFilterBackend,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter]
    filterset_class = CaseFilter
    ordering_fields = ['id', 'date', 'attend_date', 'priority']
    serializer_class = serializers.CaseSerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.CaseTemplate.objects.all().order_by('id')
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ['cidr', 'domain']
    filterset_class = CaseTemplateFilter
    ordering_fields = ['id', 'created',
                       'modified', 'cidr', 'domain', 'priority']
    serializer_class = serializers.CaseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
