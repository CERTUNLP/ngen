from rest_framework import viewsets, mixins

from ngen import models, serializers
from ngen.permissions import (
    CustomApiViewPermission,
    CustomModelPermissions,
    CustomModelPermissionsOrMinified,
)


class ArtifactViewSet(viewsets.ModelViewSet):
    queryset = models.Artifact.objects.all()
    serializer_class = serializers.ArtifactSerializer
    permission_classes = [CustomModelPermissionsOrMinified]

    def get_serializer_class(self):
        user = self.request.user

        if user.has_perm("ngen.view_minified_artifact") and not user.has_perm(
            "ngen.view_artifact"
        ):
            return serializers.ArtifactMinifiedSerializer

        return self.serializer_class


class ArtifactEnrichmentViewSet(viewsets.ModelViewSet):
    queryset = models.ArtifactEnrichment.objects.all()
    serializer_class = serializers.ArtifactEnrichmentSerializer
    permission_classes = [CustomModelPermissions]


class ArtifactRelationViewSet(viewsets.ModelViewSet):
    """
    Relation between an artifact and an object of the model (event, case, network, etc.)
    """

    queryset = models.ArtifactRelation.objects.all()
    serializer_class = serializers.ArtifactRelationSerializer
    permission_classes = [CustomModelPermissions]


class ArtifactMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Artifact.objects.all()
    serializer_class = serializers.ArtifactMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_artifact"]
