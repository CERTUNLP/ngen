import django_filters
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from ngen import models, serializers
from ngen.filters import TaxonomyFilter, PlaybookFilter, TodoTaskFilter
from ngen.permissions import (
    ActionPermission,
    CustomApiViewPermission,
    CustomModelPermissions,
)


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
    ordering_fields = [
        "id",
        "created",
        "modified",
        "name",
        "playbook",
        "priority",
        "order",
    ]
    serializer_class = serializers.TaskSerializer
    permission_classes = [CustomModelPermissions]

    action_permissions = {"move_task": "ngen.change_task"}

    @action(
        methods=["POST"],
        detail=True,
        url_path="move",
        url_name="move",
        permission_classes=[ActionPermission],
    )
    def move_task(self, request, pk=None):
        """
        Moves a task one position within its playbook `/task/<pk>/move/`,
        with {"direction": "up"} or {"direction": "down"}.
        """
        direction = request.data.get("direction")
        if direction not in ("up", "down"):
            return Response(
                {"detail": "direction must be 'up' or 'down'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = self.get_object()
        moved = task.move(up=direction == "up")

        return Response({"moved": moved}, status=status.HTTP_200_OK)


class TodoTaskViewSet(viewsets.ModelViewSet):
    queryset = models.TodoTask.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_class = TodoTaskFilter
    search_fields = ["note", "assigned_to__username", "task__name"]
    ordering_fields = [
        "id",
        "created",
        "modified",
        "completed",
        "completed_date",
        "assigned_to",
        "note",
        "task",
        "task__order",
        "task__priority__severity",
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
