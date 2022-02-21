import constance
import django_filters
from django.views.generic import TemplateView
from rest_framework import permissions, filters
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from ngen.models import Case, Network, Taxonomy, Feed, State, Behavior, \
    User, NetworkEntity, Tlp, Priority, CaseTemplate, \
    Event, Report, IncidentStateChange, Edge, Contact
from ngen.serializers import CaseSerializer, NetworkSerializer, TaxonomySerializer, FeedSerializer, \
    StateSerializer, BehaviorSerializer, UserSerializer, \
    NetworkEntitySerializer, TlpSerializer, PrioritySerializer, \
    CaseTemplateSerializer, \
    EventSerializer, ReportSerializer, IncidentStateChangeSerializer, EdgeSerializer, \
    ContactSerializer


class AboutView(TemplateView):
    html = True
    template_name = "reports/base.html"

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['html'] = True
        context['case'] = Case.objects.get(pk=161701)
        context['config'] = constance.config
        return context


class CaseViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaxonomyViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['name']
    ordering_fields = ['name']
    queryset = Taxonomy.objects.all()
    serializer_class = TaxonomySerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeedViewSet(viewsets.ModelViewSet):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    permission_classes = [permissions.IsAuthenticated]


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [permissions.IsAuthenticated]


class IncidentStateChangeViewSet(viewsets.ModelViewSet):
    queryset = IncidentStateChange.objects.all()
    serializer_class = IncidentStateChangeSerializer
    permission_classes = [permissions.IsAuthenticated]


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class BehaviorViewSet(viewsets.ModelViewSet):
    queryset = Behavior.objects.all()
    serializer_class = BehaviorSerializer
    permission_classes = [permissions.IsAuthenticated]


class TlpViewSet(viewsets.ModelViewSet):
    queryset = Tlp.objects.all()
    serializer_class = TlpSerializer
    permission_classes = [permissions.IsAuthenticated]


class PriorityViewSet(viewsets.ModelViewSet):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseTemplateViewSet(viewsets.ModelViewSet):
    queryset = CaseTemplate.objects.all()
    serializer_class = CaseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Event.objects.all()
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['case', 'taxonomy', 'network']
    filterset_fields = ['taxonomy']
    ordering_fields = ['id', 'case', 'taxonomy', 'network']
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['cidr', 'type', 'domain']
    filterset_fields = ['type']
    permission_classes = [permissions.IsAuthenticated]


class NetworkEntityViewSet(viewsets.ModelViewSet):
    queryset = NetworkEntity.objects.all()
    serializer_class = NetworkEntitySerializer
    permission_classes = [permissions.IsAuthenticated]


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
