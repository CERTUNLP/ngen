from django.db import models
from django.utils.text import slugify
from django_bleach.models import BleachField
from model_utils import Choices
from netfields import NetManager

from .utils import NgenModel, NgenTreeModel


class Taxonomy(NgenTreeModel):
    TYPE = Choices('vulnerability', 'incident')
    type = models.CharField(choices=TYPE, default=TYPE.vulnerability, max_length=20)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True)
    node_order_by = ['id']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(Taxonomy, self).save(*args, **kwargs)

    def delete(self):
        if self.get_children():
            self.get_children().update(parent=self.parent)
        super(Taxonomy, self).delete()

    def __str__(self):
        return self.name

    def get_ancestors_reports(self):
        return self.get_ancestors_related(lambda obj: obj.reports.all())

    class Meta:
        db_table = 'taxonomy'


class Report(NgenModel):
    LANG = Choices('en', 'es')
    lang = models.CharField(choices=LANG, default=LANG.en, max_length=2)
    taxonomy = models.ForeignKey('Taxonomy', models.CASCADE, related_name='reports')
    problem = BleachField()
    derived_problem = BleachField(null=True)
    verification = BleachField(null=True)
    recommendations = BleachField(null=True)
    more_information = BleachField(null=True)

    class Meta:
        db_table = 'report'
        unique_together = ['lang', 'taxonomy']

    def __str__(self):
        return "%s (%s)" % (self.taxonomy.name, self.lang)
