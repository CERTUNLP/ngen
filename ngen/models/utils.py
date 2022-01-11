from django.db import models
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
            for contact in related(ancestor):
                contacts.insert(0, contact)
        return contacts

    class Meta:
        abstract = True
