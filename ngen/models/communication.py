# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models


class Contact(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    encryption_key = models.CharField(max_length=4000, blank=True, null=True)
    network_admin = models.ForeignKey('NetworkAdmin', models.DO_NOTHING, blank=True, null=True)
    contact_type = models.CharField(max_length=255)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    priority = models.ForeignKey('IncidentPriority', models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'contact'


class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    data = models.JSONField()
    updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
    pending = models.IntegerField()
    incident = models.ForeignKey("Incident", models.DO_NOTHING, blank=True, null=True)
    discr = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'message'
