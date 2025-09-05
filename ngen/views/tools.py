import os
import time
import random
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import permissions, status, viewsets, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from constance import config
from celery.result import AsyncResult
from drf_spectacular.utils import extend_schema

from ngen import models, serializers
from ngen.utils import get_settings
from ngen.permissions import (
    CustomApiViewPermission,
    CustomMethodApiViewPermission,
    CustomModelPermissions,
)
from project import settings
from ngen.tasks import whois_lookup_task, export_events_for_email_task


class DisabledView(APIView):
    """View for disabled endpoints"""

    permission_classes = [CustomModelPermissions]

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response


class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = serializers.ContentTypeSerializer
    permission_classes = [CustomModelPermissions]


class AuditViewSet(viewsets.ModelViewSet):
    queryset = LogEntry.objects.all()
    serializer_class = serializers.AuditSerializer
    permission_classes = [CustomModelPermissions]


class ConstanceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ConstanceSerializer
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["constance.view_constance"],
        "HEAD": ["constance.view_constance"],
        "POST": ["constance.add_constance"],
        "PUT": ["constance.change_constance"],
        "PATCH": ["constance.change_constance"],
        "DELETE": ["constance.delete_constance"],
    }
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
        items = get_settings()
        item = [item for item in items if item["key"] == key]
        if not item:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"message": "Key not found."}
            )
        if not item[0]["editable"]:
            return Response(
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
                data={"message": "Key is not editable."},
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


class ExportEventsViewSet(viewsets.ViewSet):
    """
    Public viewset to export events in different formats. Runs a celery task to generate the export file.

    Required request data:
        - email (str): The email address to send the exported events to.
    """

    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        request=serializers.ExportEventsSerializer,  # lo que Swagger mostrará como body
        responses={
            202: serializers.ExportEventsSerializer
        },  # lo que Swagger mostrará como respuesta
        description="Inicia la exportación de eventos y envía el archivo por correo electrónico.",
        summary="Exportar eventos por correo electrónico",
    )
    def create(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"message": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # add random delay to avoid email enumeration attacks
        time.sleep(random.randint(1000, 5000) / 1000)
        # check if email is valid
        contact = models.Contact.objects.filter(username=email).first()
        if contact:
            export_events_for_email_task.delay(email)
        return Response(
            {
                "message": "Task to export cases launched. The exported file will be sent to the provided email address once ready."
            },
            status=status.HTTP_202_ACCEPTED,
        )


class SettingsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ConstanceSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    lookup_field = "key"
    lookup_value_regex = "[A-Za-z_][A-Za-z0-9_]*"
    valid_keys = [
        "NGEN_LANG",
        "NGEN_LANG_EXTERNAL",
        "PAGE_SIZE",
        "JWT_ACCESS_TOKEN_LIFETIME",
        "JWT_REFRESH_TOKEN_LIFETIME",
    ]

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
    permission_classes = [CustomMethodApiViewPermission]
    permission_required = {
        "GET": ["ngen.view_stringidentifier"],
        "HEAD": ["ngen.view_stringidentifier"],
        "POST": ["ngen.use_stringidentifier"],
    }

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
    permission_classes = [CustomModelPermissions]

    def get_queryset(self):
        user_pk = self.kwargs.get("pk")
        content_type = ContentType.objects.get_for_model(models.User)
        return LogEntry.objects.filter(content_type=content_type, object_id=user_pk)


class TeamLogoFileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.change_constance"]

    def put(self, request, format=None):
        file_obj = request.data["file"]

        # destination = settings.LOGO_PATH
        destination = os.path.join(settings.LOGO_PATH)

        with open(destination, "wb+") as file:
            for chunk in file_obj.chunks():
                file.write(chunk)

        config.TEAM_LOGO = destination

        return Response(status=204)


class WhoisLookupView(APIView):
    """
    Inicia la tarea de búsqueda WHOIS y devuelve el ID de la tarea.
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, ip_or_domain):
        task = whois_lookup_task.delay(ip_or_domain)
        return Response(
            {
                "task_id": task.id,
                "url": request.build_absolute_uri(
                    reverse("task_status", args=[task.id])
                ),
            },
            status=status.HTTP_202_ACCEPTED,
        )


class TaskStatusView(APIView):
    """
    Consulta el estado de la tarea dada su ID.
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, task_id):
        task_result = AsyncResult(task_id)

        if task_result.state == "PENDING":
            return Response({"status": "Pending"}, status=status.HTTP_200_OK)
        elif task_result.state != "FAILURE":
            return Response(
                {
                    "status": task_result.state,
                    "result": task_result.result,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Error al ejecutar la tarea
            return Response(
                {
                    "status": task_result.state,
                    "error": str(task_result.result),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VersionView(APIView):
    """
    View to return about the version of the application.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        version = settings.APP_VERSION_TAG
        commit = settings.APP_COMMIT
        branch = settings.APP_BRANCH
        build_file = settings.APP_BUILD_FILE
        mode = "development" if settings.DEBUG else "production"
        return Response(
            {
                "version": version,
                "commit": commit,
                "branch": branch,
                "build_file": build_file,
                "environment": mode,
            },
            status=status.HTTP_200_OK,
        )
