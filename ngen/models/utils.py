from django.db import models
from django_lifecycle import hook, BEFORE_DELETE
from model_utils.models import TimeStampedModel
from treebeard.al_tree import AL_Node


class NgenModel(TimeStampedModel):
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='+')

    class Meta:
        abstract = True


class NgenTreeModel(NgenModel, AL_Node):
    parent = models.ForeignKey('self', models.DO_NOTHING, null=True, db_index=True)

    def get_ancestors_related(self, related):
        contacts = []
        for ancestor in self.get_ancestors():
            contacts.insert(0, list(related(ancestor)))
        return contacts

    class Meta:
        abstract = True


class NgenEvidenceModel(NgenModel):
    @hook(BEFORE_DELETE)
    def delete_evidence(self):
        for evidence in self.evidence.all():
            evidence.delete()

    def evidence_path(self):
        return 'evidence/%s/%s' % (self.__class__.__name__, self.id)

    class Meta:
        abstract = True
