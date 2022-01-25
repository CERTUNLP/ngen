import re

from django.core import mail
from django.db import models
from django.template.loader import get_template
from django.utils.html import strip_tags
from django_lifecycle import hook, LifecycleModelMixin, AFTER_CREATE, AFTER_UPDATE

from .mailer import case_creation
from .utils import NgenModel


class Case(LifecycleModelMixin, NgenModel):
    tlp = models.ForeignKey('Tlp', models.DO_NOTHING)
    priority = models.ForeignKey('Priority', models.DO_NOTHING)
    date = models.DateTimeField()

    assigned = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='cases_assigned')
    state = models.ForeignKey('State', models.DO_NOTHING, related_name='cases')
    unresponded_state = models.ForeignKey('State', models.DO_NOTHING, related_name='cases_unresponded')
    unsolved_state = models.ForeignKey('State', models.DO_NOTHING, related_name='cases_unsolved')

    ltd_count = models.IntegerField()
    response_dead_line = models.DateTimeField()
    solve_dead_line = models.DateTimeField()

    report_message_id = models.CharField(max_length=255, null=True)
    raw = models.TextField(null=True)

    class Meta:
        db_table = 'case'
        ordering = ['-id']

    def contacts(self):
        contacts = []
        for event in self.events.all():
            event_contacts = list(event.network.contacts.all())
            if event_contacts:
                if event_contacts not in contacts:
                    contacts.insert(0, list(event.network.contacts.filter(priority__code__gte=self.priority.code)))
            else:
                network_contacts = event.network.get_ancestors_contacts(self.priority.code)
                if network_contacts and network_contacts[0] not in contacts:
                    contacts.insert(0, network_contacts[0])
        return contacts

    @hook(AFTER_CREATE)
    @hook(AFTER_UPDATE)
    def after_create(self):
        case_creation(case=self)

    @hook(AFTER_UPDATE, when="state", has_changed=True)
    def after_update(self):
        html_content = get_template('reports/base.html').render({'html': True, 'lang': 'es'})
        text_content = re.sub(r'\n+', '\n',
                              strip_tags(get_template('reports/base.html').render({'lang': 'es'})).replace('  ',
                                                                                                           ''))
        mail.send_mail('CASE_STATE_UPDATE', text_content, 'dude@aol.com', ['mr@lebowski.com'],
                       html_message=html_content)


class Event(LifecycleModelMixin, NgenModel):
    tlp = models.ForeignKey('Tlp', models.DO_NOTHING)
    priority = models.ForeignKey('Priority', models.DO_NOTHING)
    date = models.DateTimeField()

    taxonomy = models.ForeignKey('Taxonomy', models.DO_NOTHING)
    feed = models.ForeignKey('Feed', models.DO_NOTHING)
    reporter = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='events_reporter')
    evidence_file_path = models.CharField(max_length=255, null=True)
    notes = models.TextField(null=True)

    network = models.ForeignKey('Network', models.DO_NOTHING, null=True, related_name='events')
    case = models.ForeignKey('Case', models.CASCADE, null=True, related_name='events')

    class Meta:
        db_table = 'event'

    @hook(AFTER_UPDATE, when="case", has_changed=True)
    @hook(AFTER_CREATE)
    def after_create(self):
        if self.case:
            html_content = get_template('reports/base.html').render({'html': True, 'lang': 'es'})
            text_content = re.sub(r'\n+', '\n',
                                  strip_tags(get_template('reports/base.html').render({'lang': 'es'})).replace('  ',
                                                                                                               ''))
            mail.send_mail('EVENT_UPDATE', text_content, 'dude@aol.com', ['mr@lebowski.com'], html_message=html_content)


class CaseTemplate(NgenModel):
    taxonomy = models.ForeignKey('Taxonomy', models.DO_NOTHING)
    tlp = models.ForeignKey('Tlp', models.DO_NOTHING)
    feed = models.ForeignKey('Feed', models.DO_NOTHING)
    state = models.ForeignKey('State', models.DO_NOTHING, related_name='decision_states')
    priority = models.ForeignKey('Priority', models.DO_NOTHING)
    network = models.ForeignKey('Network', models.DO_NOTHING, db_column='network', blank=True, null=True)

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
