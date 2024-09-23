import django_filters
from django.db.models import Count
from rest_framework import filters, viewsets, mixins

from ngen import models, serializers
from ngen.filters import FeedFilter, PriorityFilter, TlpFilter
from ngen.permissions import CustomApiViewPermission, CustomModelPermissions


class FeedViewSet(viewsets.ModelViewSet):
    queryset = models.Feed.objects.annotate(events_count=Count("events")).order_by("id")
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_class = FeedFilter
    ordering_fields = ["id", "created", "modified", "name", "slug", "events_count"]
    serializer_class = serializers.FeedSerializer
    permission_classes = [CustomModelPermissions]


class PriorityViewSet(viewsets.ModelViewSet):
    queryset = models.Priority.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    filterset_class = PriorityFilter
    ordering_fields = [
        "id",
        "created",
        "modified",
        "name",
        "slug",
        "severity",
        "attend_time",
        "solve_time",
    ]
    serializer_class = serializers.PrioritySerializer
    permission_classes = [CustomModelPermissions]


class TlpViewSet(viewsets.ModelViewSet):
    queryset = models.Tlp.objects.all().order_by("id")
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    filterset_class = TlpFilter
    ordering_fields = ["id", "created", "modified", "name", "slug", "code"]
    serializer_class = serializers.TlpSerializer
    permission_classes = [CustomModelPermissions]


class FeedMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Feed.objects.all()
    serializer_class = serializers.FeedMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_feed"]


class TlpMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Tlp.objects.all()
    serializer_class = serializers.TlpMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_tlp"]


class PriorityMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Priority.objects.all()
    serializer_class = serializers.PriorityMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_priority"]
