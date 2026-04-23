import django_filters
from rest_framework import viewsets, filters, mixins
from ngen.filters import AnalyzerMappingFilter
from ngen import models, serializers
from ngen.permissions import CustomModelPermissions


class AnalyzerMappingViewSet(viewsets.ModelViewSet):
    queryset = models.AnalyzerMapping.objects.all()
    permission_classes = [CustomModelPermissions]
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["mapping_to", "mapping_from__name", "analyzer__name", "analyzer__type"]
    filterset_class = AnalyzerMappingFilter
    serializer_class = serializers.AnalyzerMappingSerializer