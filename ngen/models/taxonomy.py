# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.utils.text import slugify
from netfields import NetManager
from treebeard.al_tree import AL_Node

from ngen.models import NgenModel


class Taxonomy(NgenModel, AL_Node):
    id = models.BigAutoField(primary_key=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, null=True, db_index=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
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

    class Meta:
        db_table = 'taxonomy'


class IncidentReport(models.Model):
    slug = models.CharField(primary_key=True, max_length=64)
    lang = models.CharField(max_length=2)
    taxonomy = models.ForeignKey('Taxonomy', models.DO_NOTHING, null=True)
    problem = models.TextField()
    derivated_problem = models.TextField(blank=True, null=True)
    verification = models.TextField(blank=True, null=True)
    recomendations = models.TextField(blank=True, null=True)
    more_information = models.TextField(blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'incident_report'
