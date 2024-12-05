from rest_framework import serializers
from ngen import models
from ngen.serializers import AuditSerializerMixin


class TagSerializer(AuditSerializerMixin):
    class Meta:
        model = models.Tag
        fields = "__all__"
        read_only_fields = ["slug"]


class TagMinifiedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Tag
        fields = ["name", "slug", "color"]
        read_only_fields = ["name", "slug", "color"]
