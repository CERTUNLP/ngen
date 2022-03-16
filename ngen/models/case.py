import re
from collections import defaultdict

from constance import config
from django.core import mail
from django.db import models
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy
from django_lifecycle import hook, AFTER_CREATE, AFTER_UPDATE, BEFORE_CREATE

from . import Priority
from .utils import NgenModel, NgenEvidenceMixin, NgenTreeModel
from ..storage import HashedFilenameStorage


class Case(NgenEvidenceMixin, NgenModel):
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

    def save(self, *args, **kwargs):
        if not self.priority:
            self.priority = Priority.default_priority()
        super(Case, self).save(*args, **kwargs)

    def email_contacts(self):
        contacts = []
        for event in self.events.all():
            event_contacts = event.email_contacts()
            for contact in event_contacts:
                if contact not in contacts:
                    contacts.insert(0, contact)
        return contacts

    def events_by_contacts(self):
        contacts = defaultdict(list)
        for event in self.events.all():
            event_contacts = event.email_contacts()
            contacts[tuple(event_contacts)].append(event)
        return contacts

    @hook(AFTER_CREATE)
    def after_create(self):
        self.case_creation()

    @hook(AFTER_UPDATE, when="state", has_changed=True)
    def after_update(self):
        self.case_state_change()

    def send_mail(self, subject, template: str, from_mail: str, recipient_list: list, lang: str,
                  extra_params: dict = None):
        params = {'lang': lang, 'case': self, 'config': config}
        if extra_params:
            params.update(extra_params)
        text_content = re.sub(r'\n+', '\n', strip_tags(get_template(template).render(params)).replace('  ', ''))
        params.update({'html': True})
        html_content = get_template(template).render(params)
        mail.send_mail(subject, text_content, from_mail, recipient_list, html_message=html_content)

    def email_subject(self, subject: str):
        return '[%s][TLP:%s][ID:%s] %s' % (config.TEAM_NAME, gettext_lazy(self.tlp.name), self.id, subject)

    def communicate_assigned(self, template: str, subject, params: dict = None):
        if self.assigned and self.assigned.priority.code >= self.priority.code:
            self.send_mail(self.email_subject(subject), template, config.EMAIL_SENDER, [self.assigned.email],
                           config.NGEN_LANG, params)

    def communicate_team(self, template: str, subject: str, params: dict = None):
        if config.TEAM_EMAIL and Priority.objects.get(name=config.TEAM_EMAIL_PRIORITY).code >= self.priority.code:
            self.send_mail(self.email_subject(subject), template, config.EMAIL_SENDER, [config.TEAM_EMAIL],
                           config.NGEN_LANG, params)

    def communicate_case(self, template: str, subject: str, params: dict = None):
        for contacts, events in self.events_by_contacts().items():
            if params:
                params.update({'events': events})
            self.send_mail(self.email_subject(subject), template, config.EMAIL_SENDER,
                           [c.username for c in contacts],
                           config.NGEN_LANG, params)

    def communicate_event(self, event: 'Event', template: str, subject: str):
        self.send_mail(self.email_subject(subject), template, config.EMAIL_SENDER,
                       [c.username for c in event.email_contacts()],
                       config.NGEN_LANG, {'events': [event]})

    def communicate(self, template: str, subject: str, params: dict = None):
        self.communicate_case(template, subject, params)
        self.communicate_assigned(template, subject, params)
        self.communicate_team(template, subject, params)

    def case_creation(self):
        self.communicate('reports/base.html', gettext_lazy('New Case'))

    def case_state_change(self):
        self.communicate('reports/state_change.html', gettext_lazy('Case status updated'))

    def event_case_assign(self, event: 'Event'):
        self.communicate_event(event, 'reports/case_assign.html', gettext_lazy('New event on case'))
        self.communicate_assigned('reports/case_assign.html', gettext_lazy('New event on case'))
        self.communicate_team('reports/case_assign.html', gettext_lazy('New event on case'))


class Event(NgenEvidenceMixin, NgenTreeModel):
    tlp = models.ForeignKey('Tlp', models.DO_NOTHING)
    priority = models.ForeignKey('Priority', models.DO_NOTHING)
    date = models.DateTimeField()

    taxonomy = models.ForeignKey('Taxonomy', models.DO_NOTHING)
    feed = models.ForeignKey('Feed', models.DO_NOTHING)
    network = models.ForeignKey('Network', models.DO_NOTHING, related_name='events')

    reporter = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='events_reporter')
    evidence_file_path = models.CharField(max_length=255, null=True)
    notes = models.TextField(null=True)

    case = models.ForeignKey('Case', models.CASCADE, null=True, related_name='events')
    node_order_by = ['id']

    class Meta:
        db_table = 'event'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if not self.priority:
            self.priority = Priority.default_priority()
        super(Event, self).save(*args, **kwargs)

    @hook(BEFORE_CREATE)
    def merge(self):
        events = Event.objects.filter(taxonomy=self.taxonomy, feed=self.feed, network=self.network).order_by('id')
        self.parent = events.first()

    def add_evidence(self, file):
        if self.parent:
            self.parent.add_evidence(file)
        else:
            self.evidence.get_or_create(file=file)

    @classmethod
    def find_problems(cls):
        pass

    @classmethod
    def fix_tree(cls):
        pass

    def email_contacts(self):
        contacts = []
        priority = self.case.priority.code if self.case.priority else self.priority.code
        event_contacts = list(self.network.email_contacts(priority))
        if event_contacts:
            return event_contacts
        else:
            network_contacts = self.network.ancestors_email_contacts(priority)
            if network_contacts:
                return network_contacts[0]
        return contacts

    @hook(AFTER_UPDATE, when="case", has_changed=True, is_not=None)
    def case_assign(self):
        if self.case.events.count() >= 1:
            self.case.event_case_assign(self)


class Evidence(NgenModel):
    def directory_path(self, filename=None):
        return '%s/%s' % (self.get_related().evidence_path(), filename)

    file = models.FileField(upload_to=directory_path, null=True, storage=HashedFilenameStorage(), unique=True)

    def get_related(self):
        raise NotImplementedError()

    def __str__(self):
        return self.file.url

    def __repr__(self):
        return self.file.url

    def delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)
        self.file.storage.delete(self.file.name)

    class Meta:
        abstract = True


class EventEvidence(Evidence):
    event = models.ForeignKey('Event', models.CASCADE, null=True, related_name='evidence')

    def get_related(self):
        return self.event

    class Meta:
        db_table = 'event_evidence'


class CaseEvidence(Evidence):
    case = models.ForeignKey('Case', models.CASCADE, null=True, related_name='evidence')

    def get_related(self):
        return self.case

    class Meta:
        db_table = 'case_evidence'


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

    def save(self, *args, **kwargs):
        if not self.priority:
            self.priority = Priority.default_priority()
        super().save(*args, **kwargs)


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
