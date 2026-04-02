import django_filters
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ngen import models, serializers
from ngen.filters import AnalyzerFilter


class AnalyzerViewSet(viewsets.ModelViewSet):
    queryset = models.Analyzer.objects.all()
    serializer_class = serializers.AnalyzerSerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "type", "description"]
    filterset_class = AnalyzerFilter
    ordering_fields = ["name", "type", "enabled", "created", "modified"]

    @action(methods=["post"], detail=True, url_path="test", url_name="test")
    def test_connection(self, request, pk=None):
        analyzer = self.get_object()
        if not analyzer.enabled:
            return Response(
                {"success": False, "message": "Analyzer is disabled"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            adapter = analyzer.get_adapter()
            result = adapter.test_connection()
            http_status = status.HTTP_200_OK if result.get("success") else status.HTTP_502_BAD_GATEWAY
            return Response(result, status=http_status)
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["get"], detail=False, url_path="vuln-choices", url_name="vuln_choices")
    def vuln_choices(self, request):
        from ngen.analyzers.registry import get_vuln_choices
        return Response(get_vuln_choices())
