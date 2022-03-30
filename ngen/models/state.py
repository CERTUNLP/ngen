from django.db import models
from django.utils.text import slugify

from .utils import NgenModel


class State(NgenModel):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    blocked = models.BooleanField(default=False)
    active = models.IntegerField()
    description = models.CharField(max_length=250, null=True)
    children = models.ManyToManyField(
        "self",
        symmetrical=False,
        through='Edge',
        related_name="parents",
    )

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(State, self).save(*args, **kwargs)

    def add_child(self, child, **kwargs):
        kwargs.update({"parent": self, "child": child})
        cls = self.children.through(**kwargs)
        return cls.save()

    def remove_child(self, child=None, delete_node=False):
        if child is not None and child in self.children.all():
            self.children.through.objects.filter(parent=self, child=child).delete()
            if delete_node:
                child.delete()
        else:
            for child in self.children.all():
                self.children.through.objects.filter(parent=self, child=child).delete()
                if delete_node:
                    child.delete()

    def add_parent(self, parent, **kwargs):
        return parent.add_child(self, **kwargs)

    def remove_parent(self, parent=None, delete_node=False):
        if parent is not None and parent in self.parents.all():
            parent.children.through.objects.filter(parent=parent, child=self).delete()
            if delete_node:
                parent.delete()
        else:
            for parent in self.parents.all():
                parent.children.through.objects.filter(parent=parent, child=self).delete()
                if delete_node:
                    parent.delete()

    def siblings(self):
        return self.siblings_with_self().exclude(pk=self.pk)

    def siblings_count(self):
        return self.siblings().count()

    def siblings_with_self(self):
        return self.__class__.objects.filter(parents__in=self.parents.all()).distinct()

    def partners(self):
        return self.partners_with_self().exclude(pk=self.pk)

    def partners_count(self):
        return self.partners().count()

    def partners_with_self(self):
        return self.__class__.objects.filter(children__in=self.children.all()).distinct()

    def is_root(self):
        return bool(self.children.exists() and not self.parents.exists())

    def is_leaf(self):
        return bool(self.parents.exists() and not self.children.exists())

    def is_island(self):
        return bool(not self.children.exists() and not self.parents.exists())

    def is_sibling_of(self, ending_node):
        return ending_node in self.siblings()

    def is_partner_of(self, ending_node):
        return ending_node in self.partners()

    def is_parent_of(self, ending_node):
        return ending_node in self.children.all()

    @classmethod
    def get_initial(cls):
        return cls.objects.get(name='Initial')

    @classmethod
    def get_default(cls):
        return cls.objects.get(name='Staging')

    class Meta:
        db_table = 'state'


class Edge(NgenModel):
    parent = models.ForeignKey(State, models.CASCADE, related_name='children_edge')
    child = models.ForeignKey(State, models.CASCADE, related_name='parents_edge')
    discr = models.CharField(max_length=255)

    def __repr__(self):
        return "%s -> %s" % (self.parent, self.child)

    def __str__(self):
        return "%s -> %s" % (self.parent, self.child)

    class Meta:
        db_table = 'edge'
        unique_together = ['parent', 'child']


class IncidentStateChange(NgenModel):
    incident_id = models.IntegerField(null=True)
    responsible = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='+')
    date = models.DateTimeField(null=True)
    method = models.CharField(max_length=25)
    state_edge = models.ForeignKey('Edge', models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'incident_state_change'
