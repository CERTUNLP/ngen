from rest_framework import permissions, viewsets

from ngen import models, serializers


class StateViewSet(viewsets.ModelViewSet):
    queryset = models.State.objects.all()
    serializer_class = serializers.StateSerializer
    permission_classes = [permissions.IsAuthenticated]


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = models.Edge.objects.all()
    serializer_class = serializers.EdgeSerializer
    permission_classes = [permissions.IsAuthenticated]
