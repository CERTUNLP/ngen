from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy
from model_utils import Choices

from .utils import NgenModel


class Artifact(NgenModel):
    TYPE = Choices(('ip', 'IP'), ('domain', gettext_lazy('Domain')), (
        'url', 'Url'), ('hash', 'Hash'), ('file', gettext_lazy('File')), ('domain', gettext_lazy('Domain')))
    type = models.CharField(choices=TYPE, default=TYPE.ip, max_length=20)
    value = models.TextField()

    def __str__(self):
        display = self.value
        if self.targets.count() > 1:
            display += " (%s)" % self.targets.count()
        return display


class ArtifactRelation(NgenModel):
    artifact = models.ForeignKey('ngen.Artifact', on_delete=models.CASCADE, related_name='targets')
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='artifact_relation')
    target = GenericForeignKey()


class ArtifactRelated(models.Model):
    relations = GenericRelation('ngen.ArtifactRelation', related_query_name='%(class)ss')

    class Meta:
        abstract = True

    @property
    def artifacts(self):
        return Artifact.objects.filter(targets__in=self.artifact_relation.all())
