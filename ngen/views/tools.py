import constance
from auditlog.models import LogEntry
from rest_framework import permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView

from ngen import models, serializers
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


class DisabledView(APIView):
    """ View for disabled endpoints """
    permission_classes = (IsAuthenticated,)

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response


class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = serializers.ContentTypeSerializer


class AuditViewSet(viewsets.ModelViewSet):
    queryset = LogEntry.objects.all()
    serializer_class = serializers.AuditSerializer
    permission_classes = [permissions.IsAuthenticated]


class ConstanceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ConstanceSerializer
    permission_classes = (IsAuthenticated,)
    queryset = get_settings()
    lookup_field = 'key'
    lookup_value_regex = '[A-Za-z_][A-Za-z0-9_]*'

    def create(self, request):
        """POST - Add new"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={
            'message': 'POST method is not allowed. Use PATCH or PUT method instead to /path/<key> endpoint.'})

    def retrieve(self, request, key=None):
        """GET - Show <key>"""
        api_result = get_settings()
        result = next(
            (item for item in api_result if item["key"] == key), None)
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Key not found.'})
        return Response(result)

    def partial_update(self, request, key=None):
        """PATCH - Update <key>"""
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
        """PUT - Update <key>"""
        return self.partial_update(request, key)

    def destroy(self, request, key=None):
        """DETELE - Delete <key>"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={'message': 'DELETE method is not allowed.'})


class StringIdentifierViewSet(viewsets.ViewSet):
    serializer_class = serializers.StringIdentifierSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = serializers.StringIdentifierSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        string_identifier = serializer.save()

        return Response(string_identifier, status=status.HTTP_201_CREATED)

    def list(self, request, format=None):
        return Response(serializers.StringIdentifierSerializer().list(),
                        status=status.HTTP_200_OK)
