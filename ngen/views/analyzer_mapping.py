from rest_framework import viewsets

from ngen import models, serializers


class AnalyzerMappingViewSet(viewsets.ModelViewSet):
    queryset = models.AnalyzerMapping.objects.all()
    serializer_class = serializers.AnalyzerMappingSerializer