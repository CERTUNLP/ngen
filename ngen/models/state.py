from django.db import models
from django.utils.text import slugify

from ngen.models.common.mixins import AuditModelMixin
from ngen.utils import slugify_underscore


class State(AuditModelMixin):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    blocked = models.BooleanField(default=False)
    attended = models.BooleanField(default=False)
    solved = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=250, null=True, blank=True, default='')
    children = models.ManyToManyField(
        "self",
        symmetrical=False,
        through='Edge',
        related_name="parents",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify_underscore(self.name)
        super(State, self).save(*args, **kwargs)

    def siblings(self):
        return self.siblings_with_self().exclude(pk=self.pk)

    def siblings_with_self(self):
        return self.__class__.objects.filter(parents__in=self.parents.all()).distinct()

    def partners(self):
        return self.partners_with_self().exclude(pk=self.pk)

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


class Edge(AuditModelMixin):
    parent = models.ForeignKey(State, models.CASCADE, related_name='children_edge')
    child = models.ForeignKey(State, models.CASCADE, related_name='parents_edge')
    discr = models.CharField(max_length=255)

    def __str__(self):
        return "%s -> %s" % (self.parent, self.child)

    class Meta:
        db_table = 'edge'
        unique_together = ['parent', 'child']
