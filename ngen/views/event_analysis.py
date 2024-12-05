from rest_framework import viewsets

from ngen import models, serializers


class EventAnalysisViewSet(viewsets.ModelViewSet):
    queryset = models.EventAnalysis.objects.all()
    serializer_class = serializers.EventAnalysisSerializer