import django_filters
from rest_framework import viewsets, filters, mixins
from ngen.filters import AnalyzerMappingFilter
from ngen import models, serializers


class AnalyzerMappingViewSet(viewsets.ModelViewSet):
    queryset = models.AnalyzerMapping.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["mapping_to", "mapping_from__name", "analyzer_type"]
    filterset_class = AnalyzerMappingFilter
    serializer_class = serializers.AnalyzerMappingSerializer