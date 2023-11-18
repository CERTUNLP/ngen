import django_filters
from rest_framework import permissions, filters, viewsets

from ngen import models, serializers
from ngen.filters import TaxonomyFilter, PlaybookFilter


class TaxonomyViewSet(viewsets.ModelViewSet):
    queryset = models.Taxonomy.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ['name', 'description']
    filterset_class = TaxonomyFilter
    ordering_fields = ['id', 'created', 'modified', 'name']
    serializer_class = serializers.TaxonomySerializer
    permission_classes = [permissions.IsAuthenticated]


class PlaybookViewSet(viewsets.ModelViewSet):
    queryset = models.Playbook.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ['name', 'taxonomy__name']
    filterset_class = PlaybookFilter
    ordering_fields = ['id', 'created', 'modified', 'name', 'taxonomy__name']
    serializer_class = serializers.PlaybookSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class TodoTaskViewSet(viewsets.ModelViewSet):
    queryset = models.TodoTask.objects.all()
    serializer_class = serializers.TodoTaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = models.Report.objects.all()
    serializer_class = serializers.ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
