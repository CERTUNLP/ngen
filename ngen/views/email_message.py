import django_filters
from rest_framework import permissions, filters, viewsets
from ngen import models, serializers


class EmailMessageViewSet(viewsets.ModelViewSet):
    queryset = models.EmailMessage.objects.all().order_by("id")
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    ordering_fields = ["id", "created", "modified", "date"]
    serializer_class = serializers.EmailMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
