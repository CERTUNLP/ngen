from django.apps import apps
from django.db import models
from django_lifecycle import hook, BEFORE_DELETE, LifecycleModelMixin
from model_utils.models import TimeStampedModel
from treebeard.al_tree import AL_Node


class NgenModel(TimeStampedModel):
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='+')

    class Meta:
        abstract = True


class NgenTreeModel(AL_Node):
    @classmethod
    def find_problems(cls):
        pass

    @classmethod
    def fix_tree(cls):
        pass

    parent = models.ForeignKey('self', models.DO_NOTHING, null=True, db_index=True, related_name='children')

    def get_ancestors_related(self, related):
        contacts = []
        for ancestor in self.get_ancestors():
            contacts.insert(0, list(related(ancestor)))
        return contacts

    class Meta:
        abstract = True


class NgenMergeableModel(NgenTreeModel):

    def is_blocked(self):
        return self.state.blocked or self.is_merged()

    def is_merged(self):
        return self.parent is not None

    class Meta:
        abstract = True


class NgenEvidenceMixin(models.Model):
    @hook(BEFORE_DELETE)
    def delete_evidence(self):
        for evidence in self.evidence.all():
            evidence.delete()

    def evidence_path(self):
        return 'evidence/%s/%s' % (self.__class__.__name__, self.id)

    def add_evidence(self, file):
        self.evidence.get_or_create(file=file)

    class Meta:
        abstract = True


class NgenPriorityMixin(models.Model):
    priority = models.ForeignKey('Priority', models.DO_NOTHING)

    def save(self, *args, **kwargs):
        if not self.priority_id:
            self.priority = apps.get_model('ngen', 'Priority').default_priority()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
