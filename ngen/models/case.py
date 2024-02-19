import uuid as uuid
from collections import defaultdict
from email.utils import make_msgid
from pathlib import Path

from comment.models import Comment
from constance import config
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.mail import DNS_NAME
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_lifecycle import hook, AFTER_UPDATE, BEFORE_CREATE, BEFORE_DELETE, BEFORE_UPDATE, AFTER_CREATE
from django_lifecycle.priority import HIGHEST_PRIORITY
from model_utils import Choices
from treebeard.al_tree import AL_NodeManager

import ngen
from ngen.models.announcement import Communication
from . import Priority
from .common.mixins import MergeModelMixin, AddressModelMixin, ArtifactRelatedMixin, AuditModelMixin, \
    EvidenceModelMixin, PriorityModelMixin, ValidationModelMixin, AddressManager
from ..storage import HashedFilenameStorage

LIFECYCLE = Choices(('manual', gettext_lazy('Manual')), ('auto', gettext_lazy('Auto')), (
    'auto_open', gettext_lazy('Auto open')), ('auto_close', gettext_lazy('Auto close')))


class Case(MergeModelMixin, AuditModelMixin, PriorityModelMixin, EvidenceModelMixin, ArtifactRelatedMixin,
           Communication, ValidationModelMixin):
    tlp = models.ForeignKey('ngen.Tlp', models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, null=True, blank=True, default='')

    casetemplate_creator = models.ForeignKey('ngen.CaseTemplate', models.PROTECT, null=True, blank=True,
                                             related_name='cases_created', default=None)
    user_creator = models.ForeignKey('ngen.User', models.PROTECT, null=True, blank=True, related_name='cases_created',
                                     default=None)
    assigned = models.ForeignKey('ngen.User', models.PROTECT, null=True, related_name='assigned_cases', blank=True, default=None)
    state = models.ForeignKey('ngen.State', models.PROTECT, related_name='cases')

    attend_date = models.DateTimeField(null=True, blank=True, default=None)
    solve_date = models.DateTimeField(null=True, blank=True, default=None)

    report_message_id = models.CharField(max_length=255, null=True, blank=True, default=None)
    raw = models.TextField(null=True, blank=True, default='')
    node_order_by = ['id']

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    lifecycle = models.CharField(choices=LIFECYCLE, default=LIFECYCLE.manual, max_length=20)
    notification_count = models.PositiveSmallIntegerField(default=0)
    comments = GenericRelation(Comment)

    _temp_events = []

    class Meta:
        db_table = 'case'

    def __init__(self, *args, **kwargs):
        """ Case should receive `events` list to communicate with events on new event """
        self._temp_events = kwargs.pop('events', [])
        super().__init__(*args, **kwargs)

    def __str__(self):
        return str(self.pk)

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

    @hook(BEFORE_DELETE)
    def delete_events(self):
        for event in self.events.all():
            event.delete()

    @hook(BEFORE_CREATE)
    def before_create(self):
        if not self.date:
            self.date = self.created
        self.report_message_id = make_msgid(domain=DNS_NAME)
        if not self.state:
            self.state = ngen.models.State.get_default()
        if self.state.attended:
            self.attend_date = timezone.now()
            self.solve_date = None
        elif self.state.solved:
            self.solve_date = timezone.now()

    @hook(AFTER_CREATE)
    def after_create(self):
        if self._temp_events:
            self.events.add(*self._temp_events)
        if self.state.attended:
            self.communicate_new_open()
        else:
            if config.CASE_REPORT_NEW_CASES:
                self.communicate_new()

    @hook(BEFORE_UPDATE, when="state", has_changed=True)
    def before_update(self):
        old = self.__class__.objects.get(pk=self.pk)
        edge = ngen.models.Edge.objects.filter(parent=old.state, child=self.state).first()
        if not edge:
            raise ValidationError(
                {'state': gettext_lazy(
                    "It\'s not possible to change the state %s to %s. The new possible states are %s") % (
                              old.state, self.state, ', '.join([str(s) for s in old.state.children.all()]))})
        if self.state.attended:
            self.attend_date = timezone.now()
            self.solve_date = None
            self.communicate_open()
        elif self.state.solved:
            self.solve_date = timezone.now()
            if old.state.attended and not old.state.solved:
                self.communicate_close()
        else:
            if old.state.attended != self.state.attended or old.state.solved != self.state.solved:
                self.communicate_update()

    def communicate_new(self):
        self.communicate(gettext_lazy('New case'), 'reports/case_report.html')

    def communicate_close(self):
        self.communicate(gettext_lazy('Case closed'), 'reports/case_report.html')

    def communicate_open(self):
        title = 'Case reopened' if self.history.filter(changes__contains='solve_date":').exists() else 'Case opened'
        self.communicate(gettext_lazy(title), 'reports/case_report.html')

    def communicate_new_open(self):
        self.communicate(gettext_lazy('Case opened'), 'reports/case_report.html')

    def communicate_update(self):
        self.communicate(gettext_lazy('Case status updated'), 'reports/case_change_state.html', )

    @property
    def evidence_events(self):
        evidence = []
        for event in self.events.all():
            evidence = evidence + list(event.evidence.all())
        return evidence

    @property
    def evidence_all(self):
        return list(self.evidence.all()) + self.evidence_events

    @property
    def blocked(self):
        return self.solve_date is not None

    def merge(self, child: 'Case'):
        super().merge(child)
        for evidence in child.evidence.all():
            self.evidence.add(evidence)
        for event in child.events.all():
            self.events.add(event)
        for comment in child.comments.all():
            self.comments.add(comment)
        for artifact_relation in child.artifact_relation.all():
            self.artifact_relation.add(artifact_relation)

    @property
    def artifacts_dict(self) -> dict[str, list]:
        artifacts_dict = {'hashes': [], 'files': []}
        for evidence in self.evidence.all():
            artifacts_dict['hashes'].append(evidence.filename.split('.')[0])
            artifacts_dict['files'].append(evidence.file.path)
        return artifacts_dict

    @property
    def email_headers(self) -> dict:
        return {'Message-ID': self.report_message_id}

    @property
    def template_params(self) -> dict:
        return {'case': self, 'events': self.events.all(), 'tlp': self.tlp, 'priority': self.priority}

    @property
    def email_attachments(self) -> list[dict]:
        attachments = []
        for evidence in self.evidence_all:
            attachments.append({'name': evidence.attachment_name, 'file': evidence.file})
        return attachments

    @property
    def assigned_email(self):
        if self.assigned and self.assigned.priority.severity >= self.priority.severity:
            return self.assigned.email
        return None

    @property
    def team_email(self):
        priority = Priority.objects.get(name=config.TEAM_EMAIL_PRIORITY)
        if config.TEAM_EMAIL and priority.severity >= self.priority.severity:
            return config.TEAM_EMAIL
        return None

    def subject(self, title: str = None) -> str:
        return '[%s][TLP:%s][ID:%s] %s' % (config.TEAM_NAME, gettext_lazy(self.tlp.name), self.uuid, title)

    def communicate(self, title: str, template: str, **kwargs):
        """
        Send email to a list of recipients in 'event_by_contacts' param
        or those returned by 'event_by_contacts' method on 'to' mail header.
        Also send a copy to assigned user and team email if they are set.

        :param title: title of the email
        :param template: template to be rendered
        :param kwargs: extra params to be passed to template
        :return: None
        """
        event_by_contacts = kwargs.get('event_by_contacts', self.events_by_contacts())
        template_params = self.template_params
        recipients = self.recipients
        team_recipients = [self.assigned_email, self.team_email]
        for contacts, events in event_by_contacts.items():
            # Case has events, so send email to contacts of each event (and bcc to team)
            template_params.update({'events': events})
            recipients.update({'to': [c.username for c in contacts]})
            recipients.update({'bcc': team_recipients})
            self.send_mail(self.subject(title), self.render_template(template, extra_params=template_params),
                           recipients, self.email_attachments, self.email_headers)
        else:
            # Case has no events, so send email only to team (and assignee)
            recipients.update({'to': [recipient for recipient in team_recipients if recipient]})
            self.send_mail(self.subject(title), self.render_template(template, extra_params=self.template_params),
                           recipients, self.email_attachments, self.email_headers)
        # Increment notification_count
        # TODO: make communication a class with objects that can be audited
        self.notification_count += 1


class EventManager(AL_NodeManager, AddressManager):
    pass


class Event(MergeModelMixin, AuditModelMixin, EvidenceModelMixin, PriorityModelMixin, ArtifactRelatedMixin,
            AddressModelMixin, ValidationModelMixin):
    tlp = models.ForeignKey('ngen.Tlp', models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)

    taxonomy = models.ForeignKey('ngen.Taxonomy', models.PROTECT)
    feed = models.ForeignKey('ngen.Feed', models.PROTECT)

    reporter = models.ForeignKey('ngen.User', models.PROTECT, related_name='events_reporter')
    evidence_file_path = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True, default='')

    case = models.ForeignKey('ngen.Case', models.PROTECT, null=True, blank=True, related_name='events')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tasks = models.ManyToManyField(
        "ngen.Task",
        through='ngen.TodoTask',
        related_name="events",
    )
    node_order_by = ['id']
    comments = GenericRelation(Comment)

    objects = EventManager()

    class Meta:
        db_table = 'event'
        ordering = ['-id']

    def __str__(self):
        return "%s:%s" % (self.pk, self.address)

    @property
    def detections_count(self):
        return self.children.count() + 1

    @hook(BEFORE_CREATE, priority=HIGHEST_PRIORITY)
    def auto_merge(self):
        event = Event.get_parents().filter(taxonomy=self.taxonomy, feed=self.feed, cidr=self.cidr, domain=self.domain,
                                           case__solve_date__isnull=True).order_by('id').last()

        if event:
            if self.parent is None:
                self.parent = event

    @hook(AFTER_CREATE)
    def create_case(self):
        """ Check if case should be created and create it """
        if not self.parent:
            template = CaseTemplate.objects.parents_of(self).filter(event_taxonomy=self.taxonomy,
                                                                    event_feed=self.feed,
                                                                    active=True).first()
            if template:
                self.case = template.create_case(events=[self])

    @hook(AFTER_CREATE)
    @hook(AFTER_UPDATE, when="taxonomy", has_changed=True)
    def taxonomy_assign(self):
        self.todos.exclude(task__playbook__in=self.taxonomy.playbooks.all()).delete()
        for playbook in self.taxonomy.playbooks.all():
            for task in playbook.tasks.all():
                self.tasks.add(task)

    @hook(AFTER_UPDATE, when="case", has_changed=True, is_not=None)
    def case_assign_communication(self):
        if self.case.events.count() >= 1:
            self.case.communicate(gettext_lazy('New event on case'), 'reports/case_assign.html',
                                  event_by_contacts={tuple(self.email_contacts()): [self]})

    @property
    def blocked(self):
        if self.case:
            return self.case.blocked
        return False

    def merge(self, child: 'Event'):
        super().merge(child)
        if child.case:
            child.case = None
        for todo in child.todos.filter(completed=True):
            if self.tasks.contains(todo.task):
                self.tasks.remove(todo.task)
                self.todos.add(todo)
            else:
                todo.delete()
        for evidence in child.evidence.all():
            self.evidence.add(evidence)
        for comment in child.comments.all():
            self.comments.add(comment)
        for artifact_relation in child.artifact_relation.all():
            self.artifact_relation.add(artifact_relation)

    def email_contacts(self):
        contacts = []
        priority = self.case.priority.severity if self.case.priority else self.priority.severity
        network = ngen.models.Network.objects.parent_of(self).first()
        if network:
            event_contacts = list(network.email_contacts(priority))
            if event_contacts:
                return event_contacts
            else:
                network_contacts = network.ancestors_email_contacts(priority)
                if network_contacts:
                    return network_contacts[0]
        return contacts

    @property
    def artifacts_dict(self) -> dict:
        artifacts_dict = {'hashes': [], 'files': []}
        if self.cidr:
            artifacts_dict['ip'] = [self.address.network_address().compressed]
        if self.domain:
            artifacts_dict['domain'] = [self.domain]
        for evidence in self.evidence.all():
            artifacts_dict['hashes'].append(evidence.filename.split('.')[0])
            artifacts_dict['files'].append(evidence.file.path)
        return artifacts_dict

    @property
    def enrichable(self):
        return self.mergeable


class Evidence(AuditModelMixin, ValidationModelMixin):
    def directory_path(self, filename=None):
        return '%s/%s' % (self.get_related().evidence_path(), filename)

    file = models.FileField(upload_to=directory_path, null=True, storage=HashedFilenameStorage(), unique=True)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey()

    class Meta:
        db_table = 'evidence'

    def get_related(self):
        return self.content_object

    def __str__(self):
        return self.file.url

    @property
    def attachment_name(self):
        return '%s(%s):%s:%s' % (
            self.get_related().__class__.__name__, self.get_related().id, self.get_related().created.date(),
            self.filename)

    @property
    def filename(self):
        return Path(self.file.name).name

    def delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)
        self.file.storage.delete(self.file.name)


class CaseTemplate(AuditModelMixin, PriorityModelMixin, AddressModelMixin, ValidationModelMixin):
    event_taxonomy = models.ForeignKey('ngen.Taxonomy', models.PROTECT)
    event_feed = models.ForeignKey('ngen.Feed', models.PROTECT)

    case_tlp = models.ForeignKey('ngen.Tlp', models.PROTECT)
    case_state = models.ForeignKey('ngen.State', models.PROTECT, related_name='decision_states')
    case_lifecycle = models.CharField(choices=LIFECYCLE, default=LIFECYCLE.auto, max_length=20)

    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'case_template'

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        qs = self.__class__.objects.filter(cidr=self.cidr, domain=self.domain, event_taxonomy=self.event_taxonomy,
                                           event_feed=self.event_feed).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError('CIDR, Domain, Taxonomy, Feed tuple must be unique')

    @property
    def event_cidr(self):
        return self.cidr

    @property
    def event_domain(self):
        return self.domain

    @property
    def case_priority(self) -> 'Priority':
        return self.priority

    def create_case(self, events: list = []) -> 'Case':
        return Case.objects.create(tlp=self.case_tlp, lifecycle=self.case_lifecycle, state=self.case_state,
                                   casetemplate_creator=self, events=events)

    def matching_events_without_case(self):
        return Event.objects.children_of(self).filter(case__isnull=True, taxonomy=self.event_taxonomy,
                                    feed=self.event_feed)

    def create_cases_for_matching_events(self):
        return [self.create_case([event]) for event in self.matching_events_without_case()]

    def __str__(self):
        return str(self.id)
