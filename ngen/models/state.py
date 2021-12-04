# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models


class IncidentState(models.Model):
    slug = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    behavior = models.ForeignKey('StateBehavior', models.DO_NOTHING, db_column='behavior', blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'incident_state'


class IncidentStateChange(models.Model):
    id = models.BigAutoField(primary_key=True)
    incident_id = models.IntegerField(blank=True, null=True)
    responsable = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    date = models.DateTimeField(blank=True, null=True)
    method = models.CharField(max_length=25)
    state_edge = models.ForeignKey('StateEdge', models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'incident_state_change'


class StateBehavior(models.Model):
    slug = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=45, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    can_edit_fundamentals = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    can_edit = models.IntegerField()
    can_enrich = models.IntegerField()
    can_add_history = models.IntegerField()
    can_comunicate = models.IntegerField()
    discr = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'state_behavior'


class StateEdge(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    oldstate = models.ForeignKey(IncidentState, models.DO_NOTHING, db_column='oldState', blank=True,
                                 null=True, related_name='+')  # Field name made lowercase.
    newstate = models.ForeignKey(IncidentState, models.DO_NOTHING, db_column='newState', blank=True,
                                 null=True, related_name='+')  # Field name made lowercase.
    discr = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'state_edge'
