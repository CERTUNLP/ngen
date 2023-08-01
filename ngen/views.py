import constance
import django_filters
from auditlog.models import LogEntry
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import permissions, filters, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from ngen import models, serializers, backends
from ngen.serializers import RegisterSerializer
from ngen.utils import get_settings


class AboutView(TemplateView):
    html = True
    template_name = "reports/base.html"

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['html'] = True
        context['case'] = models.Case.objects.get(pk=161701)
        context['config'] = constance.config
        return context


class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = models.Evidence.objects.all()
    serializer_class = serializers.EvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Event.objects.all()
    filter_backends = [backends.MergedModelFilterBackend, filters.SearchFilter,
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
        backends.MergedModelFilterBackend,
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


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer


class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = serializers.ContentTypeSerializer


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


class ArtifactViewSet(viewsets.ModelViewSet):
    queryset = models.Artifact.objects.all()
    serializer_class = serializers.ArtifactSerializer
    permission_classes = [permissions.IsAuthenticated]


class ArtifactEnrichmentViewSet(viewsets.ModelViewSet):
    queryset = models.ArtifactEnrichment.objects.all()
    serializer_class = serializers.ArtifactEnrichmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ArtifactRelationViewSet(viewsets.ModelViewSet):
    """
    Relation between an artifact and an object of the model (event, case, network, etc.)
    """
    queryset = models.ArtifactRelation.objects.all()
    serializer_class = serializers.ArtifactRelationSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditViewSet(viewsets.ModelViewSet):
    queryset = LogEntry.objects.all()
    serializer_class = serializers.AuditSerializer
    permission_classes = [permissions.IsAuthenticated]
    


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = models.Announcement.objects.all()
    serializer_class = serializers.AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]


class RegisterViewSet(viewsets.ModelViewSet):
    http_method_names = ["post"]
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "success": True,
                "userID": user.id,
                "msg": "The user was successfully registered",
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidToken('No valid token found in cookie \'refresh_token\'')


class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie('refresh_token', response.data['refresh'], max_age=cookie_max_age, httponly=True,
                                path=reverse('ctoken-refresh'))
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie('refresh_token', response.data['refresh'], max_age=cookie_max_age, httponly=True,
                                path=reverse('ctoken-refresh'))
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)

    serializer_class = CookieTokenRefreshSerializer


class CookieTokenLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class DisabledView(APIView):
    """ View for disabled endpoints """
    permission_classes = (IsAuthenticated,)

    def response(self, request):
        return Response({"Failed": "Service disabled on instalation."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    get = post = put = delete = patch = head = options = response


class ConstanceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ConstanceSerializer
    permission_classes = (IsAuthenticated,)
    queryset = get_settings()
    lookup_field = 'key'
    lookup_value_regex = '[A-Za-z_][A-Za-z0-9_]*'

    def create(self, request):
        """POST - Add new user"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={'message': 'POST method is not allowed. Use PATCH or PUT method instead to /path/<key> endpoint.'})

    def retrieve(self, request, key=None):
        """GET - Show <key> user"""
        api_result = get_settings()
        result = next((item for item in api_result if item["key"] == key), None)
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Key not found.'})
        return Response(result)

    def partial_update(self, request, key=None):
        """PATCH - Update <key> user"""
        data = request.data.copy()
        data['key'] = key
        if not key in [item['key'] for item in self.queryset]:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Key not found.'})
        serializer = serializers.ConstanceSerializer(data=data)
        if serializer.is_valid():
            if key is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Key not provided.'})
            serializer.create(serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, key=None):
        """PUT - Update <key> user"""
        return self.partial_update(request, key)

    def destroy(self, request, key=None):
        """DETELE - Delete <key> user"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={'message': 'DELETE method is not allowed.'})
