# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    encryption_key = models.CharField(max_length=4000, blank=True, null=True)
    network_admin = models.ForeignKey('NetworkAdmin', models.DO_NOTHING, blank=True, null=True)
    contact_type = models.CharField(max_length=255)
    contact_case = models.ForeignKey('ContactCase', models.DO_NOTHING, db_column='contact_case', blank=True, null=True)
    discr = models.CharField(max_length=255)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contact'


class ContactCase(models.Model):
    slug = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=45, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    level = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contact_case'


class ExtTranslations(models.Model):
    locale = models.CharField(max_length=8)
    object_class = models.CharField(max_length=255)
    field = models.CharField(max_length=32)
    foreign_key = models.CharField(max_length=64)
    content = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_translations'
        unique_together = (('locale', 'object_class', 'field', 'foreign_key'),)


class Host(models.Model):
    network = models.ForeignKey('Network', models.DO_NOTHING, blank=True, null=True)
    ip = models.CharField(max_length=39, blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    slug = models.CharField(max_length=100, blank=True, null=True)
    active = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'host'


class Incident(models.Model):
    type = models.ForeignKey('IncidentType', models.DO_NOTHING, db_column='type', blank=True, null=True)
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
    origin = models.ForeignKey(Host, models.DO_NOTHING, blank=True, null=True)
    ltd_count = models.IntegerField()
    unresponded_state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='unresponded_state', blank=True,
                                          null=True, related_name='+')
    unsolved_state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='unsolved_state', blank=True,
                                       null=True, related_name='+')
    response_dead_line = models.DateTimeField(blank=True, null=True)
    solve_dead_line = models.DateTimeField(blank=True, null=True)
    priority = models.ForeignKey('IncidentPriority', models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    active = models.IntegerField()
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.
    raw = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'incident'


class IncidentComment(models.Model):
    thread = models.ForeignKey('IncidentCommentThread', models.DO_NOTHING, blank=True, null=True)
    author = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    body = models.TextField()
    ancestors = models.CharField(max_length=1024)
    depth = models.IntegerField()
    created_at = models.DateTimeField()
    state = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'incident_comment'


class IncidentCommentThread(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    incident_id = models.IntegerField(unique=True, blank=True, null=True)
    permalink = models.CharField(max_length=255)
    is_commentable = models.IntegerField()
    num_comments = models.IntegerField()
    last_comment_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'incident_comment_thread'


class IncidentDecision(models.Model):
    type = models.ForeignKey('IncidentType', models.DO_NOTHING, db_column='type', blank=True, null=True)
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
    priority = models.ForeignKey('IncidentPriority', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'incident_decision'


class IncidentDetected(models.Model):
    incident_id = models.IntegerField(blank=True, null=True)
    assigned = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    type = models.ForeignKey('IncidentType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    feed = models.ForeignKey('IncidentFeed', models.DO_NOTHING, db_column='feed', blank=True, null=True)
    state = models.ForeignKey('IncidentState', models.DO_NOTHING, db_column='state', blank=True, null=True)
    tlp_state = models.ForeignKey('IncidentTlp', models.DO_NOTHING, db_column='tlp_state', blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    evidence_file_path = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    priority = models.ForeignKey('IncidentPriority', models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    reporter = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
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
        managed = False
        db_table = 'incident_feed'


class IncidentImpact(models.Model):
    slug = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=512, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'incident_impact'


class IncidentPriority(models.Model):
    slug = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    response_time = models.IntegerField()
    solve_time = models.IntegerField()
    code = models.IntegerField()
    impact = models.ForeignKey(IncidentImpact, models.DO_NOTHING, db_column='impact', blank=True, null=True)
    urgency = models.ForeignKey('IncidentUrgency', models.DO_NOTHING, db_column='urgency', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    unresponse_time = models.IntegerField()
    unsolve_time = models.IntegerField()
    active = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'incident_priority'


class IncidentReport(models.Model):
    lang = models.CharField(max_length=2)
    type = models.ForeignKey('IncidentType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    slug = models.CharField(primary_key=True, max_length=64)
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
        managed = False
        db_table = 'incident_report'


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
        managed = False
        db_table = 'incident_state'


class IncidentStateChange(models.Model):
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
        managed = False
        db_table = 'incident_state_change'


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
        managed = False
        db_table = 'incident_tlp'


class IncidentType(models.Model):
    slug = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    is_classification = models.IntegerField(db_column='is_Classification')  # Field name made lowercase.
    taxonomyvalue = models.ForeignKey('TaxonomyValue', models.DO_NOTHING, db_column='taxonomyValue', blank=True,
                                      null=True)  # Field name made lowercase.
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'incident_type'


class IncidentUrgency(models.Model):
    slug = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=45, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'incident_urgency'


class Message(models.Model):
    data = models.JSONField()
    updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
    pending = models.IntegerField()
    incident = models.ForeignKey(Incident, models.DO_NOTHING, blank=True, null=True)
    discr = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'message'


class MigrationVersions(models.Model):
    version = models.CharField(primary_key=True, max_length=14)
    executed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'migration_versions'


class Network(models.Model):
    network_admin = models.ForeignKey('NetworkAdmin', models.DO_NOTHING, blank=True, null=True)
    network_entity = models.ForeignKey('NetworkEntity', models.DO_NOTHING, blank=True, null=True)
    ip_mask = models.IntegerField(blank=True, null=True)
    ip = models.CharField(max_length=39, blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=8, blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    ip_start_address = models.CharField(max_length=255, blank=True, null=True)
    ip_end_address = models.CharField(max_length=255, blank=True, null=True)
    asn = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'network'


class NetworkAdmin(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=100, blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'network_admin'


class NetworkEntity(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    active = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'network_entity'


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
        managed = False
        db_table = 'state_behavior'


class StateEdge(models.Model):
    mail_assigned = models.ForeignKey(ContactCase, models.DO_NOTHING, db_column='mail_assigned', blank=True, null=True,
                                      related_name='+')
    mail_team = models.ForeignKey(ContactCase, models.DO_NOTHING, db_column='mail_team', blank=True, null=True,
                                  related_name='+')
    mail_admin = models.ForeignKey(ContactCase, models.DO_NOTHING, db_column='mail_admin', blank=True, null=True,
                                   related_name='+')
    mail_reporter = models.ForeignKey(ContactCase, models.DO_NOTHING, db_column='mail_reporter', blank=True, null=True,
                                      related_name='+')
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
        managed = False
        db_table = 'state_edge'


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
        managed = False
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
        managed = False
        db_table = 'taxonomy_value'


class User(models.Model):
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
        managed = False
        db_table = 'user'
