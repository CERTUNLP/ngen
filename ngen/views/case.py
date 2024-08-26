import django_filters
from django.db.models import Count, Subquery, OuterRef, Value
from rest_framework import permissions, filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ngen import models, serializers
from ngen.filters import EventFilter, CaseFilter, CaseTemplateFilter
from ngen.views.communication_channel import BaseCommunicationChannelsViewSet


class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = models.Evidence.objects.all()
    serializer_class = serializers.EvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options', 'delete']


class EventViewSet(BaseCommunicationChannelsViewSet):
    queryset = models.Event.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["taxonomy__name", "feed__name", "address_value", "cidr", "domain", "uuid"]
    filterset_class = EventFilter
    ordering_fields = ["id", "date", "priority", "reporter", "tlp", "taxonomy", "feed", "created", "modified"]
    serializer_class = serializers.EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseViewSet(BaseCommunicationChannelsViewSet):
    queryset = models.Case.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["events__cidr", "events__domain", "name", "uuid"]
    filterset_class = CaseFilter
    ordering_fields = ["id", "date", "created", "modified", "attend_date", "solve_date", "priority", "state",
                       "casetemplate_creator", "user_creator", "assigned"]
    serializer_class = serializers.CaseSerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.CaseTemplate.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["cidr", "domain", "address_value", "event_taxonomy__name", "event_feed__name", "case_state__name"]
    filterset_class = CaseTemplateFilter
    ordering_fields = ["id", "created", "modified", "cidr", "domain", "priority", "event_taxonomy", "event_feed",
                       "case_lifecycle", "case_tlp", "case_state", "case_tlp__name", "case_state__name",
                       "event_taxonomy__name", "event_feed__name", "matching_events_without_case_count", "active"]
    serializer_class = serializers.CaseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Ugly but necessary to order by a subquery? Can be moved to a custom manager?
        ordering = self.request.query_params.get('ordering', '')
        if 'matching_events_without_case_count' in ordering:
            subquery = models.Event.objects.children_of_cidr_or_domain(
                cidr=OuterRef('cidr'), domain=OuterRef('domain')
            ).filter(
                case=None, taxonomy=OuterRef('event_taxonomy'), feed=OuterRef('event_feed')
            ).annotate(
                dummy_group_by=Value(1)  # dummy group by to count all events and avoid group by
            ).values('dummy_group_by').order_by().annotate(  # remove order by to avoid group by
                total=Count('id')
            ).values('total')[:1]
            queryset = queryset.annotate(
                matching_events_without_case_count=Subquery(subquery)
            )
        return queryset

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
    permission_classes = [permissions.IsAuthenticated]
