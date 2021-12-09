# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from model_utils.models import TimeStampedModel


class NgenModel(TimeStampedModel):
    class Meta:
        abstract = True


class Incident(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey('Taxonomy', models.DO_NOTHING, db_column='type', blank=True, null=True)
    feed = models.ForeignKey('IncidentFeed', models.DO_NOTHING, db_column='feed', blank=True, null=True)
    state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='state', blank=True, null=True,
                              related_name='+')
    network = models.ForeignKey('Network', models.DO_NOTHING, blank=True, null=True)
    reporter = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    date = models.DateTimeField()
    renotification_date = models.DateTimeField(blank=True, null=True)
    slug = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    evidence_file_path = models.CharField(max_length=255, blank=True, null=True)
    report_message_id = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    tlp_state = models.ForeignKey('IncidentTlp', models.DO_NOTHING, db_column='tlp_state', blank=True, null=True)
    assigned = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    ltd_count = models.IntegerField()
    unresponded_state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='unresponded_state', blank=True,
                                          null=True, related_name='+')
    unsolved_state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='unsolved_state', blank=True,
                                       null=True, related_name='+')
    response_dead_line = models.DateTimeField(blank=True, null=True)
    solve_dead_line = models.DateTimeField(blank=True, null=True)
    priority = models.ForeignKey('Priority', models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    active = models.IntegerField()
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.
    raw = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'incident'


class IncidentComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    thread = models.ForeignKey('IncidentCommentThread', models.DO_NOTHING, blank=True, null=True)
    author = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    body = models.TextField()
    ancestors = models.CharField(max_length=1024)
    depth = models.IntegerField()
    created_at = models.DateTimeField()
    state = models.IntegerField()

    class Meta:
        db_table = 'incident_comment'


class IncidentCommentThread(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    incident_id = models.IntegerField(unique=True, blank=True, null=True)
    permalink = models.CharField(max_length=255)
    is_commentable = models.IntegerField()
    num_comments = models.IntegerField()
    last_comment_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'incident_comment_thread'


class IncidentDecision(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey('Taxonomy', models.DO_NOTHING, db_column='type', blank=True, null=True)
    feed = models.ForeignKey('IncidentFeed', models.DO_NOTHING, db_column='feed', blank=True, null=True)
    tlp = models.ForeignKey('IncidentTlp', models.DO_NOTHING, db_column='tlp', blank=True, null=True)
    state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='state', blank=True, null=True,
                              related_name='+')
    network = models.ForeignKey('Network', models.DO_NOTHING, db_column='network', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    auto_saved = models.IntegerField()
    active = models.IntegerField()
    unresponded_state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='unresponded_state', blank=True,
                                          null=True, related_name='+')
    unsolved_state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='unsolved_state', blank=True,
                                       null=True, related_name='+')
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.
    priority = models.ForeignKey('Priority', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'incident_decision'


class IncidentDetected(models.Model):
    id = models.BigAutoField(primary_key=True)
    incident_id = models.IntegerField(blank=True, null=True)
    assigned = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    type = models.ForeignKey('Taxonomy', models.DO_NOTHING, db_column='type', blank=True, null=True)
    feed = models.ForeignKey('IncidentFeed', models.DO_NOTHING, db_column='feed', blank=True, null=True)
    state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='state', blank=True, null=True)
    tlp_state = models.ForeignKey('IncidentTlp', models.DO_NOTHING, db_column='tlp_state', blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    evidence_file_path = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    priority = models.ForeignKey('Priority', models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    reporter = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'incident_detected'


class IncidentFeed(models.Model):
    slug = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'incident_feed'


class Priority(models.Model):
    name = models.CharField(max_length=255)
    response_time = models.IntegerField()
    solve_time = models.IntegerField()
    code = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    unresponse_time = models.IntegerField()
    unsolve_time = models.IntegerField()
    active = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'priority'


class IncidentTlp(models.Model):
    slug = models.CharField(primary_key=True, max_length=45)
    rgb = models.CharField(max_length=45, blank=True, null=True)
    when = models.CharField(max_length=500, blank=True, null=True)
    encrypt = models.IntegerField(blank=True, null=True)
    why = models.CharField(max_length=500, blank=True, null=True)
    information = models.CharField(max_length=10, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'incident_tlp'


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.CharField(max_length=180)
    username = models.CharField(max_length=180)
    password = models.CharField(max_length=255)
    salt = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    api_key = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=100, blank=True, null=True)
    enabled = models.IntegerField()
    username_canonical = models.CharField(unique=True, max_length=180)
    email_canonical = models.CharField(unique=True, max_length=180)
    last_login = models.DateTimeField(blank=True, null=True)
    confirmation_token = models.CharField(unique=True, max_length=180, blank=True, null=True)
    password_requested_at = models.DateTimeField(blank=True, null=True)
    roles = models.TextField()
    created_by = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'user'
