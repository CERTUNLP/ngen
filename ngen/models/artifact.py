from constance import config
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils.translation import gettext_lazy
from model_utils import Choices

from .utils import NgenModel
from .. import tasks


class Artifact(NgenModel):
    TYPE = Choices(('ip', 'IP'), ('domain', gettext_lazy('Domain')), (
        'url', 'Url'), ('hash', 'Hash'), ('file', gettext_lazy('File')), ('domain', gettext_lazy('Domain')))
    type = models.CharField(choices=TYPE, default=TYPE.ip, max_length=20)
    value = models.CharField(blank=False, null=False, max_length=255, default=None)

    class Meta:
        db_table = 'artifact'

    def save(self, *args, **kwargs):
        super(Artifact, self).save(*args, **kwargs)
        self.enrich()

    def enrich(self):
        transaction.on_commit(lambda: tasks.enrich_artifact.delay(self.id))

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

    def save(self, *args, **kwargs):
        super(ArtifactRelated, self).save(*args, **kwargs)
        self.artifact_update()

    def artifact_update(self):
        self.artifact_relation.all().delete()
        for artifact_type, artifact_value in self.artifacts_dict.items():
            if artifact_type in config.ALLOWED_ARTIFACTS_TYPES.split(','):
                artifact, created = Artifact.objects.get_or_create(type=artifact_type, value=artifact_value)
                ArtifactRelation.objects.get_or_create(artifact=artifact,
                                                       content_type=ContentType.objects.get_for_model(self),
                                                       object_id=self.id)
                if not created:
                    artifact.enrich()

    @property
    def artifacts_dict(self) -> dict:
        raise NotImplementedError


class ArtifactEnrichment(NgenModel):
    artifact = models.ForeignKey(Artifact, on_delete=models.CASCADE, related_name='enrichments')
    name = models.CharField(max_length=100)
    success = models.BooleanField(default=True)
    raw = models.JSONField()

    def __str__(self):
        return "%s: %s(%s)" % (self.artifact, self.name, self.success)

    class Meta:
        db_table = 'artifact_enrichment'
        unique_together = ['artifact', 'name']
