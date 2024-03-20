import django_filters
from rest_framework import permissions, filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ngen import models, serializers, backends
from ngen.filters import EventFilter, CaseFilter, CaseTemplateFilter


class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = models.Evidence.objects.all()
    serializer_class = serializers.EvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Event.objects.all()
    filter_backends = [
        backends.MergedModelFilterBackend,
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["taxonomy__name", "feed__name", "address_value", "cidr", "domain"]
    filterset_class = EventFilter
    ordering_fields = ["id", "date", "priority", "reporter", "tlp", "taxonomy", "feed", "created"]
    serializer_class = serializers.EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseViewSet(viewsets.ModelViewSet):
    queryset = models.Case.objects.all()
    filter_backends = [
        backends.MergedModelFilterBackend,
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["events__cidr", "events__domain"]
    filterset_class = CaseFilter
    ordering_fields = ["id", "date", "attend_date", "priority"]
    serializer_class = serializers.CaseSerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.CaseTemplate.objects.all().order_by("id")
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["cidr", "domain", "address_value"]
    filterset_class = CaseTemplateFilter
    ordering_fields = ["id", "created", "modified", "cidr", "domain", "priority", "taxonomy"]
    serializer_class = serializers.CaseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['GET'], detail=True, url_path='create-cases', url_name='create_cases')
    def create_cases(self, request, pk=None):
        """
        Process matching events without parent/case to this template `/template/<pk>/process-events/`.
        """
        template = self.get_object()
        cases = template.create_cases_for_matching_events()
        return Response(
            serializers.CaseSerializer(cases, many=True, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class CaseMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.Case.objects.all()
    serializer_class = serializers.CaseMinifiedSerializer
    pagination_class = None
