import datetime
import uuid as uuid
from collections import defaultdict
from email.utils import make_msgid
from pathlib import Path

from comment.models import Comment
from constance import config
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.mail import DNS_NAME
from django.db import models
from django.utils.translation import gettext_lazy
from django_lifecycle import hook, AFTER_UPDATE, BEFORE_CREATE, BEFORE_DELETE, BEFORE_UPDATE, AFTER_CREATE
from django_lifecycle.priority import HIGHEST_PRIORITY
from model_utils import Choices

import ngen
from . import ArtifactRelated, Priority
from .utils import NgenModel, NgenEvidenceMixin, NgenPriorityMixin, NgenMergeableModel, NgenAddressModel
from ..communication import Communication
from ..storage import HashedFilenameStorage

LIFECYCLE = Choices(('manual', gettext_lazy('Manual')), ('auto', gettext_lazy('Auto')), (
    'auto_open', gettext_lazy('Auto open')), ('auto_close', gettext_lazy('Auto close')))


class Case(NgenMergeableModel, NgenModel, NgenPriorityMixin, NgenEvidenceMixin, ArtifactRelated, Communication):
    tlp = models.ForeignKey('ngen.Tlp', models.DO_NOTHING)
    date = models.DateTimeField()

    assigned = models.ForeignKey('ngen.User', models.DO_NOTHING, null=True, related_name='assigned_cases')
    state = models.ForeignKey('ngen.State', models.DO_NOTHING, related_name='cases')

    attend_date = models.DateTimeField(null=True)
    solve_date = models.DateTimeField(null=True)

    report_message_id = models.CharField(max_length=255, null=True)
    raw = models.TextField(null=True)
    node_order_by = ['id']

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    lifecycle = models.CharField(choices=LIFECYCLE, default=LIFECYCLE.manual, max_length=20)
    notification_count = models.PositiveSmallIntegerField(default=1)
    comments = GenericRelation(Comment)

    class Meta:
        db_table = 'case'

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
            self.attend_date = datetime.datetime.now()
            self.solve_date = None
        elif self.state.solved:
            self.solve_date = datetime.datetime.now()

    @hook(AFTER_CREATE)
    def after_create(self):
        self.communicate(gettext_lazy('New Case'), 'reports/case_base.html')

    @hook(BEFORE_UPDATE, when="state", has_changed=True)
    def before_update(self):
        if self.state.attended:
            self.attend_date = datetime.datetime.now()
            self.solve_date = None
            self.communicate_open()
        elif self.state.solved:
            self.solve_date = datetime.datetime.now()
            self.communicate_close()
        else:
            self.communicate(gettext_lazy('Case status updated'), 'reports/state_change.html', )

    def communicate_close(self):
        self.communicate(gettext_lazy('Case closed'), 'reports/case_base.html')

    def communicate_open(self):
        title = 'Case reopened' if self.history.filter(changes__contains='solve_date":').exists() else 'Case opened'
        self.communicate(gettext_lazy(title), 'reports/case_base.html')

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
        event_by_contacts = kwargs.get('event_by_contacts', self.events_by_contacts().items())
        template_params = self.template_params
        recipients = self.recipients
        team_recipients = [self.assigned_email, self.team_email]
        if event_by_contacts:
            for contacts, events in event_by_contacts:
                template_params.update({'events': events})
                recipients.update({'to': [c.username for c in contacts]})
                recipients.update({'bcc': team_recipients})
                self.send_mail(self.subject(title), self.render_template(template, extra_params=template_params),
                               recipients, self.email_attachments, self.email_headers)
        else:
            recipients.update({'to': [recipient for recipient in team_recipients if recipient]})
            self.send_mail(self.subject(title), self.render_template(template, extra_params=self.template_params),
                           recipients, self.email_attachments, self.email_headers)


class Event(NgenMergeableModel, NgenModel, NgenEvidenceMixin, NgenPriorityMixin, ArtifactRelated, NgenAddressModel):
    tlp = models.ForeignKey('ngen.Tlp', models.DO_NOTHING)
    date = models.DateTimeField()

    taxonomy = models.ForeignKey('ngen.Taxonomy', models.DO_NOTHING)
    feed = models.ForeignKey('ngen.Feed', models.DO_NOTHING)

    reporter = models.ForeignKey('ngen.User', models.DO_NOTHING, null=True, related_name='events_reporter')
    evidence_file_path = models.CharField(max_length=255, null=True)
    notes = models.TextField(null=True)

    case = models.ForeignKey('ngen.Case', models.DO_NOTHING, null=True, related_name='events')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tasks = models.ManyToManyField(
        "ngen.Task",
        through='ngen.TodoTask',
        related_name="events",
    )
    node_order_by = ['id']
    comments = GenericRelation(Comment)

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
            self.parent = event
        else:
            template = CaseTemplate.objects.parents_of(self).filter(event_taxonomy=self.taxonomy,
                                                                    event_feed=self.feed).first()
            if template:
                self.case = template.create_case()

    @hook(AFTER_UPDATE, when="taxonomy", has_changed=True)
    def taxonomy_assign(self):
        self.todos.exclude(task__playbook__in=self.taxonomy.playbooks.all()).delete()
        for playbook in self.taxonomy.playbooks.all():
            for task in playbook.tasks.all():
                self.tasks.add(task)

    @hook(AFTER_UPDATE, when="case", has_changed=True, is_not=None)
    def case_assign_communication(self, event: 'Event'):
        if event.case.events.count() >= 1:
            event.case.communicate(gettext_lazy('New event on case'), 'reports/case_assign.html',
                                   event_by_contacts={tuple(event.email_contacts()): [event]})

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
        network = ngen.models.Network.lookup_parent(self)
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
            artifacts_dict['ip'] = [self.cidr.network_address]
        if self.domain:
            artifacts_dict['domain'] = [self.domain]
        for evidence in self.evidence.all():
            artifacts_dict['hashes'].append(evidence.filename.split('.')[0])
            artifacts_dict['files'].append(evidence.file.path)
        return artifacts_dict

    @property
    def enrichable(self):
        return self.mergeable


class Evidence(NgenModel):
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


class CaseTemplate(NgenModel, NgenPriorityMixin, NgenAddressModel):
    event_taxonomy = models.ForeignKey('ngen.Taxonomy', models.DO_NOTHING)
    event_feed = models.ForeignKey('ngen.Feed', models.DO_NOTHING)

    case_tlp = models.ForeignKey('ngen.Tlp', models.DO_NOTHING)
    case_state = models.ForeignKey('ngen.State', models.DO_NOTHING, related_name='decision_states')
    case_lifecycle = models.CharField(choices=LIFECYCLE, default=LIFECYCLE.auto, max_length=20)

    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'case_template'

    def save(self, *args, **kwargs):
        if not self.cidr and not self.domain:
            default_network = ngen.models.Network.objects.default_network()
            self.cidr = default_network.cidr
            self.domain = default_network.domain
        super(CaseTemplate, self).save()

    @property
    def event_cidr(self):
        return self.cidr

    @property
    def event_domain(self):
        return self.domain

    @property
    def case_priority(self) -> 'Priority':
        return self.priority

    def create_case(self) -> 'Case':
        return Case.objects.create(tlp=self.case_tlp, lifecycle=self.case_lifecycle, state=self.case_state)

    def __str__(self):
        return str(self.id)


class ActiveSession(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
