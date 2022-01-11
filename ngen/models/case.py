from django.db import models
from model_utils.models import TimeStampedModel


class NgenModel(TimeStampedModel):
    class Meta:
        abstract = True


class Case(NgenModel):
    tlp = models.ForeignKey('Tlp', models.DO_NOTHING)
    state = models.ForeignKey('State', models.DO_NOTHING, related_name='incidents')
    priority = models.ForeignKey('Priority', models.DO_NOTHING)
    assigned = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='incidents_assigned')
    reporter = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='incidents_reporter')
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='incidents_createdby')
    date = models.DateTimeField()

    network = models.ForeignKey('Network', models.DO_NOTHING)

    unresponded_state = models.ForeignKey('State', models.DO_NOTHING, related_name='incidents_unresponded')
    unsolved_state = models.ForeignKey('State', models.DO_NOTHING, related_name='incidents_unsolved')
    ltd_count = models.IntegerField()
    response_dead_line = models.DateTimeField(null=True)
    solve_dead_line = models.DateTimeField(null=True)

    report_message_id = models.CharField(max_length=255, null=True)
    raw = models.TextField(null=True)

    class Meta:
        db_table = 'case'


class Event(NgenModel):
    taxonomy = models.ForeignKey('Taxonomy', models.DO_NOTHING)
    tlp = models.ForeignKey('Tlp', models.DO_NOTHING)
    feed = models.ForeignKey('Feed', models.DO_NOTHING)
    priority = models.ForeignKey('Priority', models.DO_NOTHING)
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='events_createdby')
    reporter = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='events_reporter')
    date = models.DateTimeField()
    evidence_file_path = models.CharField(max_length=255, null=True)
    notes = models.TextField(null=True)

    # network = models.ForeignKey('Network', models.DO_NOTHING)
    case = models.ForeignKey('Case', models.CASCADE)

    class Meta:
        db_table = 'event'


class CaseTemplate(NgenModel):
    taxonomy = models.ForeignKey('Taxonomy', models.DO_NOTHING)
    tlp = models.ForeignKey('Tlp', models.DO_NOTHING)
    feed = models.ForeignKey('Feed', models.DO_NOTHING)
    state = models.ForeignKey('State', models.DO_NOTHING, related_name='decision_states')
    priority = models.ForeignKey('Priority', models.DO_NOTHING)
    network = models.ForeignKey('Network', models.DO_NOTHING, db_column='network', blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True)

    active = models.BooleanField(default=True)
    unresponded_state = models.ForeignKey('State', models.DO_NOTHING, related_name='decision_unresponded_states')
    unsolved_state = models.ForeignKey('State', models.DO_NOTHING, related_name='decision_unsolved_states')

    class Meta:
        db_table = 'case_template'


class IncidentComment(models.Model):
    thread = models.ForeignKey('IncidentCommentThread', models.DO_NOTHING, blank=True, null=True)
    author = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    body = models.TextField()
    ancestors = models.CharField(max_length=1024)
    depth = models.IntegerField()
    created = models.DateTimeField()
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
