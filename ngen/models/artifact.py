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
    value = models.CharField(blank=False, null=False, max_length=255, default=None)

    class Meta:
        db_table = 'artifact'

    def __str__(self):
        display = '%s: %s' % (self.type, self.value)
        if self.artifact_relation.count() > 1:
            display += " (%s)" % self.artifact_relation.count()
        return display

    @property
    def related_list(self):
        targets = []
        for artifact_relation in self.artifact_relation.all():
            targets.append(artifact_relation.related)
        return targets


class ArtifactRelation(NgenModel):
    artifact = models.ForeignKey('ngen.Artifact', on_delete=models.CASCADE, related_name='artifact_relation')
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='artifact_relation')
    related = GenericForeignKey()

    class Meta:
        db_table = 'artifact_relation'
        unique_together = ['artifact', 'object_id', 'content_type']

    def __str__(self):
        return "%s -> %s: %s" % (self.artifact, self.content_type.name, self.related)


class ArtifactRelated(models.Model):
    artifact_relation = GenericRelation('ngen.ArtifactRelation', related_query_name='%(class)ss')

    class Meta:
        abstract = True

    @property
    def artifacts(self):
        return Artifact.objects.filter(artifact_relation__in=self.artifact_relation.all())
