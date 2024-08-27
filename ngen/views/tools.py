import constance
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from ngen import models, serializers
from ngen.utils import get_settings


class AboutView(TemplateView):
    html = True
    template_name = "reports/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["html"] = True
        context["case"] = models.Case.objects.get(pk=161701)
        context["config"] = constance.config
        return context


class DisabledView(APIView):
    """View for disabled endpoints"""

    permission_classes = [permissions.IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response


class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = serializers.ContentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditViewSet(viewsets.ModelViewSet):
    queryset = LogEntry.objects.all()
    serializer_class = serializers.AuditSerializer
    permission_classes = [permissions.IsAuthenticated]


class ConstanceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ConstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "key"
    lookup_value_regex = "[A-Za-z_][A-Za-z0-9_]*"

    def get_queryset(self):
        """GET - List all instances"""
        return get_settings()

    def create(self, request):
        """POST - Add new"""
        return Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            data={
                "message": "POST method is not allowed. Use PATCH or PUT method instead to /path/<key> endpoint."
            },
        )

    def retrieve(self, request, key=None):
        """GET - Show <key>"""
        result = next((item for item in get_settings() if item["key"] == key), None)
        if result is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"message": "Key not found."}
            )
        return Response(result)

    def partial_update(self, request, key=None):
        """PATCH - Update <key>"""
        data = request.data.copy()
        data["key"] = key
        if not key in [item["key"] for item in get_settings()]:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"message": "Key not found."}
            )
        serializer = serializers.ConstanceSerializer(data=data)
        if serializer.is_valid():
            if key is None:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"message": "Key not provided."},
                )
            serializer.create(serializer.validated_data)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, key=None):
        """PUT - Update <key>"""
        return self.partial_update(request, key)

    def destroy(self, request, key=None):
        """DETELE - Delete <key>"""
        return Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            data={"message": "DELETE method is not allowed."},
        )


class SettingsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ConstanceSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "key"
    lookup_value_regex = "[A-Za-z_][A-Za-z0-9_]*"
    valid_keys = ["NGEN_LANG", "NGEN_LANG_EXTERNAL"]

    def get_queryset(self):
        """GET - List all instances"""
        return [item for item in get_settings() if item["key"] in self.valid_keys]

    def retrieve(self, request, key=None):
        """GET - Show <key>"""
        result = next(
            (item for item in self.get_queryset() if item["key"] == key), None
        )
        if result is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"message": "Key not found."}
            )
        return Response(result)


class StringIdentifierViewSet(viewsets.ViewSet):
    serializer_class = serializers.StringIdentifierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = serializers.StringIdentifierSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        string_identifier = serializer.save()

        return Response(string_identifier, status=status.HTTP_201_CREATED)

    def list(self, request, format=None):
        return Response(
            serializers.StringIdentifierSerializer().list(), status=status.HTTP_200_OK
        )


class UserAuditsListView(viewsets.ModelViewSet):
    serializer_class = serializers.AuditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get("pk")
        content_type = ContentType.objects.get_for_model(models.User)
        return LogEntry.objects.filter(content_type=content_type, object_id=user_pk)
