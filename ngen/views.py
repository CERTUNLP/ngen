import constance
import django_filters
from django.views.generic import TemplateView
from rest_framework import permissions, filters
from rest_framework import viewsets

from ngen import models, serializers, backends


class AboutView(TemplateView):
    html = True
    template_name = "reports/base.html"

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['html'] = True
        context['case'] = models.Case.objects.get(pk=161701)
        context['config'] = constance.config
        return context


class CaseEvidenceViewSet(viewsets.ModelViewSet):
    queryset = models.CaseEvidence.objects.all()
    serializer_class = serializers.CaseEvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventEvidenceViewSet(viewsets.ModelViewSet):
    queryset = models.EventEvidence.objects.all()
    serializer_class = serializers.EventEvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Event.objects.all()
    filter_backends = [backends.EventRootFilterBackend, filters.SearchFilter,
                       django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter]
    search_fields = ['case', 'taxonomy', 'network']
    filterset_fields = ['taxonomy']
    ordering_fields = ['id', 'case', 'taxonomy', 'network']
    serializer_class = serializers.EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseViewSet(viewsets.ModelViewSet):
    queryset = models.Case.objects.all()
    filter_backends = [
        # filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter]
    # search_fields = ['taxonomy', 'network']
    # filterset_fields = ['taxonomy']
    ordering_fields = ['id']
    serializer_class = serializers.CaseSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaxonomyViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['name']
    ordering_fields = ['name']
    queryset = models.Taxonomy.objects.all()
    serializer_class = serializers.TaxonomySerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = models.Report.objects.all()
    serializer_class = serializers.ReportSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeedViewSet(viewsets.ModelViewSet):
    queryset = models.Feed.objects.all()
    serializer_class = serializers.FeedSerializer
    permission_classes = [permissions.IsAuthenticated]


class StateViewSet(viewsets.ModelViewSet):
    queryset = models.State.objects.all()
    serializer_class = serializers.StateSerializer
    permission_classes = [permissions.IsAuthenticated]


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = models.Edge.objects.all()
    serializer_class = serializers.EdgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class TlpViewSet(viewsets.ModelViewSet):
    queryset = models.Tlp.objects.all()
    serializer_class = serializers.TlpSerializer
    permission_classes = [permissions.IsAuthenticated]


class PriorityViewSet(viewsets.ModelViewSet):
    queryset = models.Priority.objects.all()
    serializer_class = serializers.PrioritySerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.CaseTemplate.objects.all()
    serializer_class = serializers.CaseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = models.Network.objects.all()
    serializer_class = serializers.NetworkSerializer
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['cidr', 'type', 'domain']
    filterset_fields = ['type']
    permission_classes = [permissions.IsAuthenticated]


class NetworkEntityViewSet(viewsets.ModelViewSet):
    queryset = models.NetworkEntity.objects.all()
    serializer_class = serializers.NetworkEntitySerializer
    permission_classes = [permissions.IsAuthenticated]


class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class PlaybookViewSet(viewsets.ModelViewSet):
    queryset = models.Playbook.objects.all()
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
