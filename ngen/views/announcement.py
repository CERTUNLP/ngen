from rest_framework import viewsets

from ngen import models, serializers
from ngen.permissions import CustomModelPermissions


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = models.Announcement.objects.all()
    serializer_class = serializers.AnnouncementSerializer
    permission_classes = [CustomModelPermissions]
