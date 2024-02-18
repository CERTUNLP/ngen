import django_filters
from rest_framework import permissions, filters, viewsets
from ngen import models, serializers


class CommunicationChannelViewSet(viewsets.ModelViewSet):
    """
    CommunicationChannelViewSet class
    """

    queryset = models.CommunicationChannel.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["id", "name", "message_id"]
    ordering_fields = ["id", "created", "modified", "name", "message_id"]
    serializer_class = serializers.CommunicationChannelSerializer
    permission_classes = [permissions.IsAuthenticated]
