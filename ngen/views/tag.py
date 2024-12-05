import django_filters
from rest_framework import viewsets, filters, mixins

from ngen import models, serializers
from ngen.permissions import CustomModelPermissions, CustomApiViewPermission


class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "color", "slug"]
    ordering_fields = [
        "name",
        "slug",
        "color",
    ]
    serializer_class = serializers.TagSerializer
    permission_classes = [CustomModelPermissions]


class TagMinifiedViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "color", "slug"]
    ordering_fields = [
        "name",
        "slug",
        "color",
    ]
    serializer_class = serializers.TagMinifiedSerializer
    permission_classes = [CustomModelPermissions]


class TagMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_tag"]
