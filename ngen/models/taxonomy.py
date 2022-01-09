from django.db import models
from django.utils.text import slugify
from model_utils import Choices
from netfields import NetManager
from treebeard.al_tree import AL_Node

from ngen.models import NgenModel


class Taxonomy(NgenModel, AL_Node):
    parent = models.ForeignKey('self', models.DO_NOTHING, null=True, db_index=True)
    TYPE = Choices('vulnerability', 'incident')
    type = models.CharField(choices=TYPE, default=TYPE.vulnerability, max_length=20)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True)
    objects = NetManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(Taxonomy, self).save(*args, **kwargs)

    def delete(self):
        if self.get_children():
            self.get_children().update(parent=self.parent)
        super(Taxonomy, self).delete()

    @classmethod
    def find_problems(cls):
        pass

    @classmethod
    def fix_tree(cls):
        pass

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'taxonomy'


class Report(NgenModel):
    LANG = Choices('en', 'es')
    lang = models.CharField(choices=LANG, default=LANG.en, max_length=2)
    taxonomy = models.ForeignKey('Taxonomy', models.CASCADE)
    problem = models.TextField()
    derived_problem = models.TextField(null=True)
    verification = models.TextField(null=True)
    recommendations = models.TextField(null=True)
    more_information = models.TextField(null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'report'
        unique_together = ['lang', 'taxonomy']

    def __repr__(self):
        return "%s-%s" % (self.taxonomy.name, self.lang)

    def __str__(self):
        return "%s-%s" % (self.taxonomy.name, self.lang)
