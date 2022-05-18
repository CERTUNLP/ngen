import datetime
import uuid as uuid
from collections import defaultdict
from email.utils import make_msgid
from pathlib import Path

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import DNS_NAME
from django.db import models
from django.utils.translation import gettext_lazy
from django_lifecycle import hook, AFTER_UPDATE, BEFORE_CREATE, BEFORE_DELETE, BEFORE_UPDATE
from model_utils import Choices

import ngen
from . import ArtifactRelated
from .utils import NgenModel, NgenEvidenceMixin, NgenPriorityMixin, NgenMergeableModel, NgenAddressModel
from ..storage import HashedFilenameStorage


class Case(NgenMergeableModel, NgenModel, NgenPriorityMixin, NgenEvidenceMixin, ArtifactRelated):
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
    LIFECYCLE = Choices(('manual', gettext_lazy('Manual')), ('auto', gettext_lazy('Auto')), (
        'auto_open', gettext_lazy('Auto open')), ('auto_close', gettext_lazy('Auto close')))
    lifecycle = models.CharField(choices=LIFECYCLE, default=LIFECYCLE.manual, max_length=20)
    notification_count = models.PositiveSmallIntegerField(default=0)

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
        self.report_message_id = make_msgid(domain=DNS_NAME)
        if not self.state:
            self.state = ngen.models.State.get_default()

    @hook(BEFORE_UPDATE, when="state", has_changed=True)
    def after_update(self):
        if self.state.attended:
            self.attend_date = datetime.datetime.now()
            self.solve_date = None
        if self.state.solved:
            self.solve_date = datetime.datetime.now()

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

    @property
    def artifacts_dict(self) -> dict:
        artifacts_dict = {'hashes': [], 'files': []}
        for evidence in self.evidence.all():
            artifacts_dict['hashes'].append(evidence.filename.split('.')[0])
            artifacts_dict['files'].append(evidence.file.path)
        return artifacts_dict

    @property
    def attachments(self):
        evidence = []
        for evidence in self.evidence_all:
            evidence.append({'name': evidence.attachment_name, 'file': evidence.file.read()})
        return evidence


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

    class Meta:
        db_table = 'event'
        ordering = ['-id']

    def __str__(self):
        return "%s:%s" % (self.pk, self.address)

    @hook(BEFORE_CREATE)
    def auto_merge(self):
        event = Event.get_parents().filter(taxonomy=self.taxonomy, feed=self.feed, cird=self.cidr, domain=self.domain,
                                           case__solve_date__isnull=True).order_by('id').last()
        if event:
            event.merge(self)

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
        child.tasks.clear()
        for evidence in child.evidence.all():
            self.evidence.add(evidence)

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

    @hook(AFTER_UPDATE, when="taxonomy", has_changed=True)
    def taxonomy_assign(self):
        self.todos.exclude(task__playbook__in=self.taxonomy.playbooks.all()).delete()
        for playbook in self.taxonomy.playbooks.all():
            for task in playbook.tasks.all():
                self.tasks.add(task)

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


class CaseTemplate(NgenModel, NgenPriorityMixin):
    taxonomy = models.ForeignKey('ngen.Taxonomy', models.DO_NOTHING)
    tlp = models.ForeignKey('ngen.Tlp', models.DO_NOTHING)
    feed = models.ForeignKey('ngen.Feed', models.DO_NOTHING)
    state = models.ForeignKey('ngen.State', models.DO_NOTHING, related_name='decision_states')
    network = models.ForeignKey('ngen.Network', models.DO_NOTHING, db_column='network', blank=True, null=True)

    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'case_template'


class IncidentComment(models.Model):
    thread = models.ForeignKey('ngen.IncidentCommentThread', models.DO_NOTHING, blank=True, null=True)
    author = models.ForeignKey('ngen.User', models.DO_NOTHING, blank=True, null=True)
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
