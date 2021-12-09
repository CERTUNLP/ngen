# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from netfields import NetManager
from treebeard.al_tree import AL_Node

from ngen.models import NgenModel


class IncidentType(NgenModel, AL_Node):
    name = models.CharField(max_length=100)
    slug = models.CharField(primary_key=True, max_length=100)
    active = models.BooleanField()
    description = models.CharField(max_length=250, blank=True, null=True)
    taxonomyvalue = models.ForeignKey('TaxonomyValue', models.DO_NOTHING, db_column='taxonomyValue', blank=True,
                                      null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, null=True, db_index=True)
    objects = NetManager()

    @classmethod
    def find_problems(cls):
        pass

    @classmethod
    def fix_tree(cls):
        pass

    class Meta:
        db_table = 'incident_type'


class TaxonomyPredicate(models.Model):
    slug = models.CharField(primary_key=True, max_length=100)
    description = models.CharField(max_length=1024)
    expanded = models.CharField(max_length=255)
    version = models.IntegerField()
    value = models.CharField(unique=True, max_length=255)
    updated_at = models.DateTimeField(blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'taxonomy_predicate'


class TaxonomyValue(models.Model):
    slug = models.CharField(primary_key=True, max_length=100)
    description = models.CharField(max_length=1024)
    expanded = models.CharField(max_length=255)
    value = models.CharField(unique=True, max_length=255)
    updated_at = models.DateTimeField(blank=True, null=True)
    version = models.IntegerField()
    taxonomypredicate = models.ForeignKey(TaxonomyPredicate, models.DO_NOTHING, db_column='taxonomyPredicate',
                                          blank=True, null=True)  # Field name made lowercase.
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'taxonomy_value'


class IncidentReport(models.Model):
    slug = models.CharField(primary_key=True, max_length=64)
    lang = models.CharField(max_length=2)
    type = models.ForeignKey('IncidentType', models.DO_NOTHING, db_column='type', blank=True, null=True)
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
