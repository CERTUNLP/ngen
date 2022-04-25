from auditlog.models import AuditlogHistoryField
from django.apps import apps
from django.db import models
from django.utils.translation import gettext
from django_lifecycle import hook, BEFORE_DELETE, BEFORE_UPDATE
from model_utils.models import TimeStampedModel
from rest_framework.exceptions import ValidationError
from treebeard.al_tree import AL_Node


class NgenModel(TimeStampedModel):
    history = AuditlogHistoryField()

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

    def get_ancestors_related(self, callback, flat=False):
        return self.get_related(self.get_ancestors, callback, flat)

    def get_descendants_related(self, callback, flat=False):
        return self.get_related(self.get_descendants, callback, flat)

    @staticmethod
    def get_related(related_callback, callback, flat=False):
        related = []
        for ancestor in related_callback():
            results = callback(ancestor)
            if results:
                if flat:
                    for result in results:
                        related.insert(0, result)
                else:
                    related.insert(0, results)
        return related

    @classmethod
    def get_parents(cls):
        return cls.objects.filter(parent__isnull=True)

    class Meta:
        abstract = True

    def is_child(self):
        return self.parent is not None

    def is_parent(self):
        return self.children.exists()


class NgenMergeableModel(NgenTreeModel):

    def is_blocked(self) -> bool:
        raise NotImplementedError

    def is_mergeable(self) -> bool:
        return not self.is_merged() and not self.is_blocked()

    def is_merged(self) -> bool:
        return self.is_child()

    def is_mergeable_with(self, child: 'NgenMergeableModel') -> bool:
        return child is not self and child.is_mergeable() and self.is_mergeable()

    def merge(self, child: 'NgenMergeableModel'):
        if self.is_mergeable_with(child):
            raise ValidationError({'parent': gettext('The parent must not be the same instance.')})

    @hook(BEFORE_UPDATE, when="parent", has_changed=True, is_not=None)
    def parent_changed(self):
        self.parent.merge(self)

    @hook(BEFORE_DELETE)
    def delete_children(self):
        for child in self.get_descendants():
            child.delete()

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
