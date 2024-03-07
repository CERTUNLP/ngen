from rest_framework import permissions, viewsets

from ngen import models, serializers


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


class ArtifactMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.Artifact.objects.all()
    serializer_class = serializers.ArtifactMinifiedSerializer
    pagination_class = None
