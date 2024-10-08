import django_filters
from rest_framework import filters, viewsets, mixins

from ngen import models, serializers
from ngen.filters import TaxonomyFilter, PlaybookFilter
from ngen.permissions import CustomApiViewPermission, CustomModelPermissions


class TaxonomyViewSet(viewsets.ModelViewSet):
    queryset = models.Taxonomy.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = [
        "name",
        "description",
        "slug",
        "group__name",
        "group__slug",
        "alias_of__name",
        "alias_of__slug",
    ]
    filterset_class = TaxonomyFilter
    ordering_fields = [
        "id",
        "created",
        "modified",
        "name",
        "reports",
        "group__name",
        "alias_of__name",
        "needs_review",
        "type",
        "active",
    ]
    serializer_class = serializers.TaxonomySerializer
    permission_classes = [CustomModelPermissions]


class TaxonomyGroupViewSet(viewsets.ModelViewSet):
    queryset = models.TaxonomyGroup.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description", "slug"]
    ordering_fields = [
        "id",
        "created",
        "modified",
        "name",
        "taxonomies",
        "needs_review",
    ]
    serializer_class = serializers.TaxonomyGroupSerializer
    permission_classes = [CustomModelPermissions]


class PlaybookViewSet(viewsets.ModelViewSet):
    queryset = models.Playbook.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "taxonomy__name"]
    filterset_class = PlaybookFilter
    ordering_fields = ["id", "created", "modified", "name", "taxonomy__name"]
    serializer_class = serializers.PlaybookSerializer
    permission_classes = [CustomModelPermissions]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "created", "modified", "name", "playbook", "priority"]
    serializer_class = serializers.TaskSerializer
    permission_classes = [CustomModelPermissions]


class TodoTaskViewSet(viewsets.ModelViewSet):
    queryset = models.TodoTask.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["note", "assigned_to__username"]
    ordering_fields = [
        "id",
        "created",
        "modified",
        "completed",
        "assigned_to",
        "note",
        "reports",
    ]
    serializer_class = serializers.TodoTaskSerializer
    permission_classes = [CustomModelPermissions]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = models.Report.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["taxonomy__name"]
    ordering_fields = [
        "id",
        "created",
        "modified",
        "problem",
        "derived_problem",
        "taxonomy",
        "verification",
        "recommendations",
        "more_information",
        "lang",
        "taxonomy__name",
    ]
    serializer_class = serializers.ReportSerializer
    permission_classes = [CustomModelPermissions]


class TaxonomyMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Taxonomy.objects.all()
    serializer_class = serializers.TaxonomyMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_taxonomy"]


class TaxonomyGroupMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.TaxonomyGroup.objects.all()
    serializer_class = serializers.TaxonomyGroupMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_taxonomygroup"]
