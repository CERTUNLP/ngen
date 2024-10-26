import django_filters
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Subquery, OuterRef, Value
from django.utils.translation import gettext_lazy
from rest_framework import filters, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from ngen import models, serializers
from ngen.filters import EventFilter, CaseFilter, CaseTemplateFilter
from ngen.tasks import create_cases_for_matching_events
from ngen.views.communication_channel import BaseCommunicationChannelsViewSet
from ngen.permissions import (
    CustomApiViewPermission,
    CustomMethodApiViewPermission,
    CustomModelPermissions,
)


class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = models.Evidence.objects.all()
    serializer_class = serializers.EvidenceSerializer
    permission_classes = [CustomModelPermissions]
    http_method_names = ["get", "post", "head", "options", "delete"]


class NetworkAdminEvidenceViewSet(EvidenceViewSet):
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["ngen.view_evidence_network_admin"],
        "HEAD": ["ngen.view_evidence_network_admin"],
        "POST": ["ngen.add_evidence_network_admin"],
        "DELETE": ["ngen.delete_evidence_network_admin"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # Obtener el content type del modelo relacionado (Network en este caso)
        event_ct = ContentType.objects.get(model="event")
        case_ct = ContentType.objects.get(model="case")
        print(event_ct, case_ct)
        events = models.Event.objects.filter(network__contacts__user=user).values_list(
            "id", flat=True
        )
        cases = models.Case.objects.filter(
            events__network__contacts__user=user
        ).values_list("id", flat=True)
        return (
            queryset.filter(content_type=event_ct, object_id__in=events)
            | queryset.filter(content_type=case_ct, object_id__in=cases)
        ).distinct()


class EventViewSet(BaseCommunicationChannelsViewSet):
    queryset = models.Event.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = [
        "taxonomy__name",
        "feed__name",
        "address_value",
        "cidr",
        "domain",
        "uuid",
        "tags__name",
    ]
    filterset_class = EventFilter
    ordering_fields = [
        "id",
        "date",
        "priority",
        "reporter",
        "tlp",
        "taxonomy",
        "feed",
        "created",
        "modified",
        "tags__name",
    ]
    serializer_class = serializers.EventSerializer
    permission_classes = [CustomModelPermissions]


class NetworkAdminEventViewSet(EventViewSet):
    serializer_class = serializers.NetworkAdminEventSerializer
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["ngen.view_event_network_admin"],
        "HEAD": ["ngen.view_event_network_admin"],
        "POST": ["ngen.add_event_network_admin"],
        "PUT": ["ngen.change_event_network_admin"],
        "PATCH": ["ngen.change_event_network_admin"],
        "DELETE": ["ngen.delete_event_network_admin"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(network__contacts__user=user).distinct()


class CaseViewSet(BaseCommunicationChannelsViewSet):
    queryset = models.Case.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["events__cidr", "events__domain", "name", "uuid"]
    filterset_class = CaseFilter
    ordering_fields = [
        "id",
        "date",
        "created",
        "modified",
        "attend_date",
        "solve_date",
        "priority",
        "state",
        "casetemplate_creator",
        "user_creator",
        "assigned",
    ]
    serializer_class = serializers.CaseSerializer
    permission_classes = [CustomModelPermissions]


class NetworkAdminCaseViewSet(CaseViewSet):
    serializer_class = serializers.NetworkAdminCaseSerializer
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["ngen.view_case_network_admin"],
        "HEAD": ["ngen.view_case_network_admin"],
        "POST": ["ngen.add_case_network_admin"],
        "PUT": ["ngen.change_case_network_admin"],
        "PATCH": ["ngen.change_case_network_admin"],
        "DELETE": ["ngen.delete_case_network_admin"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(events__network__contacts__user=user).distinct()


class CaseTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.CaseTemplate.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = [
        "cidr",
        "domain",
        "address_value",
        "event_taxonomy__name",
        "event_feed__name",
        "case_state__name",
    ]
    filterset_class = CaseTemplateFilter
    ordering_fields = [
        "id",
        "created",
        "modified",
        "cidr",
        "domain",
        "priority",
        "event_taxonomy",
        "event_feed",
        "case_lifecycle",
        "case_tlp",
        "case_state",
        "case_tlp__name",
        "case_state__name",
        "event_taxonomy__name",
        "event_feed__name",
        "matching_events_without_case_count",
        "active",
    ]
    serializer_class = serializers.CaseTemplateSerializer
    permission_classes = [CustomModelPermissions]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Ugly but necessary to order by a subquery? Can be moved to a custom manager?
        ordering = self.request.query_params.get("ordering", "")
        if "matching_events_without_case_count" in ordering:
            subquery = (
                models.Event.objects.children_of_cidr_or_domain(
                    cidr=OuterRef("cidr"), domain=OuterRef("domain")
                )
                .filter(
                    case=None,
                    taxonomy=OuterRef("event_taxonomy"),
                    feed=OuterRef("event_feed"),
                )
                .annotate(
                    dummy_group_by=Value(
                        1
                    )  # dummy group by to count all events and avoid group by
                )
                .values("dummy_group_by")
                .order_by()
                .annotate(total=Count("id"))  # remove order by to avoid group by
                .values("total")[:1]
            )
            queryset = queryset.annotate(
                matching_events_without_case_count=Subquery(subquery)
            )
        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="create-cases",
        url_name="create_cases",
        permission_classes=[CustomModelPermissions],
    )
    def create_cases(self, request, pk=None):
        """
        Process matching events without parent/case to this template `/template/<pk>/process-events/`.
        """
        template = self.get_object()
        create_cases_for_matching_events.delay(template.pk)
        return Response(
            {"message": gettext_lazy("Task create cases for matching events launched")},
            status=status.HTTP_200_OK,
        )


class CaseMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Case.objects.all()
    serializer_class = serializers.CaseMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_case"]
