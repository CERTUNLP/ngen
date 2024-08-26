from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models, transaction
from django.utils.translation import gettext_lazy
from model_utils import Choices

from ngen.models.common.mixins import AuditModelMixin, ValidationModelMixin
from .. import tasks


class Artifact(AuditModelMixin, ValidationModelMixin):
    TYPE = Choices(
        ("ip", "IP"),
        ("domain", gettext_lazy("Domain")),
        ("fqdn", gettext_lazy("FQDN")),
        ("url", "Url"),
        ("mail", gettext_lazy("Mail")),
        ("hash", "Hash"),
        ("file", gettext_lazy("File")),
        ("other", gettext_lazy("Other")),
        ("user-agent", gettext_lazy("User agent")),
        ("autonomous-system", gettext_lazy("Autonomous system")),
    )
    type = models.CharField(choices=TYPE, default=TYPE.ip, max_length=20)
    value = models.CharField(blank=False, null=False, max_length=255, unique=True)

    class Meta:
        db_table = "artifact"
        ordering = ["id"]

    def save(self, *args, **kwargs):
        super(Artifact, self).save(*args, **kwargs)
        self.enrich()

    def enrich(self):
        transaction.on_commit(lambda: tasks.enrich_artifact.delay(self.id))

    def __str__(self):
        return f"{self.type}: {self.value} ({self.artifact_relation.count()})"

    @property
    def related(self):
        targets = []
        for artifact_relation in self.artifact_relation.all().order_by("object_id"):
            targets.append(artifact_relation.related)
        return targets


class ArtifactRelation(AuditModelMixin, ValidationModelMixin):
    artifact = models.ForeignKey(
        "ngen.Artifact", on_delete=models.CASCADE, related_name="artifact_relation"
    )
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="artifact_relation"
    )
    object_id = models.PositiveIntegerField()
    related = GenericForeignKey("content_type", "object_id")
    auto_created = models.BooleanField(
        default=False,
        help_text=gettext_lazy(
            "Designates whether this relation was created automatically and may will be removed "
            "automatically when the related object is modified."
        ),
    )

    class Meta:
        db_table = "artifact_relation"
        unique_together = ["artifact", "object_id", "content_type"]

    def __str__(self):
        return f"{self.artifact} -> {self.content_type.name}: {self.related}"

    def clean_fields(self, exclude=None):
        try:
            # Check if related object exists
            obj = self.content_type.get_object_for_this_type(id=self.object_id)
            parent = getattr(obj, "parent", None)
            if parent:
                # If object has parent, add artifact to his parent also
                ar = ArtifactRelation(
                    artifact=self.artifact,
                    content_type=self.content_type,
                    object_id=parent.id,
                    auto_created=True,
                )
                ar.save()
        except ObjectDoesNotExist as e:
            raise ValidationError("Related object not exists.")
        super().clean_fields(exclude=exclude)


class ArtifactEnrichment(AuditModelMixin, ValidationModelMixin):
    artifact = models.ForeignKey(
        Artifact, on_delete=models.CASCADE, related_name="enrichments"
    )
    name = models.CharField(max_length=255)
    success = models.BooleanField(default=True)
    raw = models.JSONField()

    def __str__(self):
        return "%s: %s(%s)" % (self.artifact, self.name, self.success)

    class Meta:
        db_table = "artifact_enrichment"
        unique_together = ["artifact", "name"]
