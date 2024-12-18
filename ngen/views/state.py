import django_filters
from rest_framework import viewsets, filters, mixins

from ngen import models, serializers
from ngen.filters import StateFilter
from ngen.permissions import (
    CustomApiViewPermission,
    CustomModelPermissions,
    CustomModelPermissionsOrMinified,
)


class StateViewSet(viewsets.ModelViewSet):
    queryset = models.State.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_class = StateFilter
    ordering_fields = [
        "id",
        "created",
        "modified",
        "name",
        "blocked",
        "attended",
        "solved",
        "active",
    ]
    serializer_class = serializers.StateSerializer
    permission_classes = [CustomModelPermissionsOrMinified]

    def get_serializer_class(self):
        user = self.request.user

        if user.has_perm("ngen.view_minified_state") and not user.has_perm(
            "ngen.view_state"
        ):
            return serializers.StateMinifiedSerializer

        return self.serializer_class


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = models.Edge.objects.all()
    serializer_class = serializers.EdgeSerializer
    permission_classes = [CustomModelPermissions]


class StateMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.State.objects.all()
    serializer_class = serializers.StateMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_state"]
