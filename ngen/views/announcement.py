from rest_framework import permissions, viewsets

from ngen import models, serializers


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = models.Announcement.objects.all()
    serializer_class = serializers.AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
