import re
from typing import Collection
import uuid as uuid
from collections import defaultdict
from datetime import timedelta, datetime
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
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_lifecycle import (
    hook,
    AFTER_UPDATE,
    BEFORE_CREATE,
    BEFORE_DELETE,
    BEFORE_UPDATE,
    AFTER_CREATE,
)
from django_lifecycle.priority import HIGHEST_PRIORITY
from model_utils import Choices
from treebeard.al_tree import AL_NodeManager
from taggit.managers import TaggableManager
from django.apps import apps

import ngen
from ngen.models.announcement import Communication
from ngen.utils import clean_list, get_mime_type
from . import Priority
from .common.mixins import (
    MergeModelMixin,
    AddressModelMixin,
    ArtifactRelatedMixin,
    AuditModelMixin,
    EvidenceModelMixin,
    PriorityModelMixin,
    ValidationModelMixin,
    AddressManager,
    ChannelableMixin,
    # TaggedItemMixin,
)
from ..storage import HashedFilenameStorage

LIFECYCLE = Choices(
    ("manual", gettext_lazy("Manual")),
    ("auto", gettext_lazy("Auto")),
    ("auto_open", gettext_lazy("Auto open")),
    ("auto_close", gettext_lazy("Auto close")),
)


class Case(
    MergeModelMixin,
    AuditModelMixin,
    PriorityModelMixin,
    EvidenceModelMixin,
    ArtifactRelatedMixin,
    Communication,
    ValidationModelMixin,
    ChannelableMixin,
    # TaggedItemMixin,
):
    tlp = models.ForeignKey("ngen.Tlp", models.PROTECT)
    date = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255, null=True, blank=True, default="")

    casetemplate_creator = models.ForeignKey(
        "ngen.CaseTemplate",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="cases_created",
        default=None,
    )
    user_creator = models.ForeignKey(
        "ngen.User",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="cases_created",
        default=None,
    )
    assigned = models.ForeignKey(
        "ngen.User",
        models.PROTECT,
        null=True,
        related_name="assigned_cases",
        blank=True,
        default=None,
    )
    state = models.ForeignKey("ngen.State", models.PROTECT, related_name="cases")

    attend_date = models.DateTimeField(null=True, blank=True, default=None)
    solve_date = models.DateTimeField(null=True, blank=True, default=None)

    report_message_id = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    raw = models.TextField(null=True, blank=True, default="")
    node_order_by = ["id"]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    lifecycle = models.CharField(
        choices=LIFECYCLE, default=LIFECYCLE.manual, max_length=20
    )
    notification_count = models.PositiveSmallIntegerField(default=0)
    comments = GenericRelation(Comment)
    tags = TaggableManager(through="ngen.TaggedObject", blank=True)

    _temp_events = []

    class Meta:
        db_table = "case"
        permissions = [
            ("view_case_network_admin", "Can view case as network admin"),
            ("add_case_network_admin", "Can add case as network admin"),
            ("change_case_network_admin", "Can change case as network admin"),
            ("delete_case_network_admin", "Can delete case as network admin"),
        ]

    def __init__(self, *args, **kwargs):
        """Case should receive `events` list to communicate with events on new event"""
        self._temp_events = kwargs.pop("_temp_events", []) + kwargs.pop("events", [])
        super().__init__(*args, **kwargs)

    def __str__(self):
        return str(self.pk)

    @property
    def evidence_case(self):
        return list(self.evidence.all())

    @property
    def evidence_events(self):
        evidence = []
        for event in self.events.all():
            evidence = evidence + list(event.evidence.all())
        return evidence

    @property
    def evidence_all(self):
        return self.evidence_case + self.evidence_events

    @property
    def blocked(self):
        """
        Case is blocked if was on a blocked state and is still on a blocked state.
        This allows to edit the case when state changes to blocked and allows to edit the case when state changes from
        blocked to an unblocked state.
        """
        return (
            ngen.models.State.objects.get(pk=self.initial_value("state")).blocked
            and self.state.blocked
        )

    @property
    def artifacts_dict(self) -> dict[str, list]:
        artifacts_dict = {"hashes": [], "files": []}
        for evidence in self.evidence.all():
            artifacts_dict["hashes"].append(evidence.filename.split(".")[0])
            artifacts_dict["files"].append(evidence.file.path)
        return artifacts_dict

    @property
    def email_headers(self) -> dict:
        return {"Message-ID": self.report_message_id}

    @property
    def template_params(self) -> dict:
        return {
            "case": self,
            "events": self.events.all(),
            "tlp": self.tlp,
            "priority": self.priority,
        }

    @property
    def email_attachments(self) -> list[dict]:
        attachments = []
        for evidence in self.evidence_all:
            attachments.append(
                {
                    "name": evidence.attachment_name,
                    "file": evidence.directory_path(evidence.filename),
                }
            )
        return attachments

    def get_attachments_for_events(self, events):
        attachments = {}
        for event in events:
            for evidence in event.evidence.all():
                attachments[evidence.id] = {
                    "name": evidence.attachment_name,
                    "file": evidence.file,
                }
        return attachments.values()

    def get_attachments_for_events_v2(self, events):
        attachments = []
        for event in events:
            for evidence in event.evidence.all():
                attachments.append(
                    {
                        "name": evidence.attachment_name,
                        "file": evidence.directory_path(evidence.filename),
                    }
                )
        return attachments

    @property
    def assigned_email(self):
        if self.assigned and self.assigned.priority.severity >= self.priority.severity:
            return self.assigned.email
        return None

    def get_team_email_by_priority(self):
        """
        Get the team email if the priority (config.TEAM_EMAIL_PRIORITY) is
        greater than or equal to the case priority.
        Used by get_internal_contacts() method to send emails to the team on
        bcc.
        :return: team email or None
        """
        priority = Priority.objects.get(name=config.TEAM_EMAIL_PRIORITY)
        if config.TEAM_EMAIL and priority.severity >= self.priority.severity:
            return config.TEAM_EMAIL
        return None

    @hook(BEFORE_DELETE)
    def delete_events(self):
        for event in self.events.all():
            event.delete()

    @hook(BEFORE_CREATE)
    def before_create(self):
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
        edge = ngen.models.Edge.objects.filter(
            parent=old.state, child=self.state
        ).first()
        if not edge:
            raise ValidationError(
                {
                    "state": gettext_lazy(
                        "It's not possible to change the state %s to %s. The new possible states are %s"
                    )
                    % (
                        old.state,
                        self.state,
                        ", ".join([str(s) for s in old.state.children.all()]),
                    )
                }
            )
        if self.state.attended:
            self.attend_date = timezone.now()
            self.solve_date = None
            self.communicate_open()
        elif self.state.solved:
            self.solve_date = timezone.now()
            if old.state.attended and not old.state.solved:
                self.communicate_close()
        else:
            if (
                old.state.attended != self.state.attended
                or old.state.solved != self.state.solved
            ):
                self.communicate_update()

    def merge(self, child: "Case", save_child: bool = True):
        super().merge(child, save_child)
        for evidence in child.evidence.all():
            self.evidence.add(evidence)
        for event in child.events.all():
            self.events.add(event)
        for comment in child.comments.all():
            self.comments.add(comment)
        for artifact_relation in child.artifact_relation.all():
            self.artifact_relation.add(artifact_relation)

    def email_contacts(self):
        contacts = []
        for event in self.events.all():
            event_contacts = event.email_contacts()
            for contact in event_contacts:
                if contact not in contacts:
                    contacts.insert(0, contact)
        return contacts

    def events_by_contacts(self):
        """
        Organizes events by their associated contacts.
        This method iterates through all events and groups them based on their email contacts.
        Each unique set of email contacts will have a list of events associated with it.
        Returns:
            defaultdict: A dictionary where the keys are frozensets of email contacts and the values are lists of events.
        Example:
            {
                (contact1, contact2): [event1, event4],
                (): [event2],
                (contact1): [event3],
            }
        """

        contacts = defaultdict(list)
        for event in self.events.all():
            event_contacts = event.email_contacts()
            contacts.setdefault(frozenset(event_contacts), []).append(event)
        return contacts

    def communicate_new(self):
        self.communicate_v2("case_report")

    def communicate_close(self):
        self.communicate_v2("case_closed_report")

    def communicate_open(self):
        self.communicate_v2("case_report")

    def communicate_new_open(self):
        self.communicate_v2("case_report")

    def communicate_update(self):
        self.communicate_v2("case_change_state")

    def subject(self, title: str = None) -> str:
        return "[%s][TLP:%s][ID:%s] %s" % (
            config.TEAM_NAME,
            self.tlp.name.upper(),
            self.uuid,
            title,
        )

    def subject_v2(self, channel_type: str = None) -> str:
        channel_section = f"[{channel_type.upper()}]" if channel_type else ""
        return f"[{config.TEAM_NAME}][TLP:{self.tlp.name.upper()}]{channel_section} Case ID: {self.uuid}"

    # def communicate(self, title: str, template: str, attachments=True, **kwargs):
    #     """
    #     Send email to a list of recipients in 'event_by_contacts' param
    #     or those returned by 'event_by_contacts' method on 'to' mail header.
    #     Also send a copy to assigned user and team email if they are set.

    #     :param title: title of the email
    #     :param template: template to be rendered
    #     :param kwargs: extra params to be passed to template
    #     :return: None
    #     """
    #     event_by_contacts = kwargs.get("event_by_contacts", self.events_by_contacts())
    #     template_params = self.template_params
    #     recipients = self.recipients
    #     team_recipients = [
    #         mail for mail in [self.assigned_email, self.get_team_email_by_priority()] if mail
    #     ]

    #     for contacts, events in event_by_contacts.items():
    #         # Case has events, so send email to contacts of each event (and bcc to team)
    #         template_params.update({"events": events})
    #         recipients.update({"to": [c.username for c in contacts]})
    #         recipients.update({"bcc": team_recipients})
    #         self.send_mail(
    #             self.subject(title),
    #             self.render_template(template, extra_params=template_params),
    #             recipients,
    #             self.get_attachments_for_events(events) if attachments else [],
    #             self.email_headers,
    #         )

    #     if not event_by_contacts or frozenset() in event_by_contacts.keys():
    #         # Case has no events or there is events without contacts, so send email to team and assignee with those events
    #         template_params.update({"events": event_by_contacts.get((), [])})
    #         recipients.update(
    #             {"to": [recipient for recipient in team_recipients if recipient]}
    #         )
    #         self.send_mail(
    #             self.subject(title),
    #             self.render_template(template, extra_params=self.template_params),
    #             recipients,
    #             self.email_attachments,
    #             self.email_headers,
    #         )
    #     # Increment notification_count
    #     # TODO: make communication a class with objects that can be audited
    #     self.notification_count += 1

    def communicate_v2(
        self,
        template: str,
        events: Collection["Event"] = None,
        send_attachments: bool = True,
    ):
        """
        Communicate V2
        Send email to the communication channels of all the events
        associated with the case.

        Send email to the intern communication channel of the case.

        :param title: title of the email
        :param template: path of template to be rendered
        """
        if self._temp_events:
            self.events.add(*self._temp_events)

        template_params = self.template_params

        # Communicates on the channels of each event of the case
        for event in events or self.events.all():
            # If there is no channel with affected contacts, create one
            ngen.models.CommunicationChannel.get_or_create_channel_with_affected(
                channelable=event
            )

            event_channels = event.communication_channels.all()

            # Communicates on each each channel of the event
            for channel in event_channels:
                channel.communicate(
                    subject=self.subject_v2("AFFECTED"),
                    template=template,
                    template_params=template_params,
                    bcc_recipients=self.get_internal_contacts(),
                    attachments=(
                        self.get_attachments_for_events_v2([event])
                        if send_attachments
                        else []
                    ),
                )

        intern_channel = (
            ngen.models.CommunicationChannel.get_or_create_channel_with_intern(
                channelable=self
            )
        )
        intern_channel.communicate(
            subject=self.subject_v2("INTERN"),
            template=template,
            template_params=template_params,
            attachments=self.email_attachments if send_attachments else [],
        )
        self.notification_count += 1

    def get_internal_contacts(self):
        """
        Returns a list of internal contacts of the case.
        """
        # this function is not using get_team_email_by_priority() because can
        # return None and this is not the expected behavior
        return clean_list([self.assigned_email, config.TEAM_EMAIL])

    def get_affected_contacts(self):
        contacts_from_all_events = []
        for event in self.events.all():
            contacts_from_all_events.append(event.get_affected_contacts())

        return contacts_from_all_events

    def get_reporter_contacts(self):
        reporters_from_all_events = []
        for event in self.events.all():
            reporters_from_all_events.append(event.get_reporter_contacts())

        return reporters_from_all_events


class EventManager(AL_NodeManager, AddressManager):
    pass


class Event(
    MergeModelMixin,
    AuditModelMixin,
    EvidenceModelMixin,
    PriorityModelMixin,
    ArtifactRelatedMixin,
    AddressModelMixin,
    ValidationModelMixin,
    ChannelableMixin,
    # TaggedItemMixin,
):
    tlp = models.ForeignKey("ngen.Tlp", models.PROTECT)
    date = models.DateTimeField(default=timezone.now)

    network = models.ForeignKey(
        "ngen.Network",
        models.PROTECT,
        null=True,
        blank=True,
        related_name="events",
        editable=False,
    )

    taxonomy = models.ForeignKey("ngen.Taxonomy", models.PROTECT, related_name="events")
    feed = models.ForeignKey("ngen.Feed", models.PROTECT, related_name="events")
    initial_taxonomy_slug = models.CharField(
        max_length=255, null=True, blank=True, default="", editable=False
    )

    reporter = models.ForeignKey(
        "ngen.User", models.PROTECT, related_name="events_reporter"
    )
    evidence_file_path = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True, default="")

    case = models.ForeignKey(
        "ngen.Case", models.PROTECT, null=True, blank=True, related_name="events"
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tasks = models.ManyToManyField(
        "ngen.Task",
        through="ngen.TodoTask",
        related_name="events",
    )
    node_order_by = ["id"]
    comments = GenericRelation(Comment)
    tags = TaggableManager(through="ngen.TaggedObject", blank=True)

    objects = EventManager()

    class Meta:
        db_table = "event"
        ordering = ["-id"]
        permissions = [
            ("view_event_network_admin", "Can view event as network admin"),
            ("add_event_network_admin", "Can add event as network admin"),
            ("change_event_network_admin", "Can change event as network admin"),
            ("delete_event_network_admin", "Can delete event as network admin"),
            ("can_mark_event_as_solved", "Can mark an event as solved"),
            ("can_retest_event", "Can retest an event"),
        ]

    def __str__(self):
        return "%s:%s" % (self.pk, self.address)

    @property
    def detections_count(self):
        return self.children.count() + 1

    @property
    def blocked(self):
        if self.case:
            return self.case.blocked
        return False

    @property
    def artifacts_dict(self) -> dict:
        artifacts_dict = {"hashes": [], "files": []}
        if self.cidr:
            artifacts_dict["ip"] = [self.address.network_address().compressed]
        if self.domain:
            artifacts_dict["domain"] = [self.domain]
        for evidence in self.evidence.all():
            artifacts_dict["hashes"].append(evidence.filename.split(".")[0])
            artifacts_dict["files"].append(evidence.file.path)
        return artifacts_dict

    @property
    def enrichable(self):
        return self.mergeable

    @property
    def template_params(self) -> dict:
        return {
            "case": self.case,
            "events": [self],
            "tlp": self.case.tlp,
            "priority": self.case.priority,
        }

    @property
    def evidence_all(self):
        case_evidence = self.case.evidence.all() if self.case else []
        return list(self.evidence.all()) + list(case_evidence)

    @property
    def email_attachments(self) -> list[dict]:
        attachments = []
        for evidence in self.evidence_all:
            attachments.append(
                {"name": evidence.attachment_name, "file": evidence.file}
            )
        return attachments

    def update_taxonomy(self):
        if self.taxonomy:
            if not self.initial_taxonomy_slug:
                self.initial_taxonomy_slug = self.taxonomy.slug
            if self.taxonomy.alias_of:
                self.taxonomy = self.taxonomy.alias_of

    @hook(BEFORE_CREATE, priority=HIGHEST_PRIORITY)
    def auto_merge(self):
        self.update_taxonomy()
        if config.AUTO_MERGE_EVENTS:
            extra_filters = {}
            if config.AUTO_MERGE_BY_FEED:
                extra_filters.update({"feed": self.feed})
            if config.AUTO_MERGE_TIME_WINDOW_MINUTES:
                minutes_limit = config.AUTO_MERGE_TIME_WINDOW_MINUTES
                date_limit = datetime.now() - timedelta(minutes=minutes_limit)
                extra_filters.update({"date__gte": date_limit})

            # This will find the last event that is not merged and has the same cidr, domain and taxonomy
            # If this event is blocked it will not be merged
            event = (
                self.__class__.objects.filter(
                    Q(case__isnull=True) | Q(case__state__blocked=False),
                    parent__isnull=True,
                    cidr=self.cidr,
                    domain=self.domain,
                    taxonomy=self.taxonomy,
                    **extra_filters,
                )
                .order_by("id")
                .last()
            )

            # Check if event is mergeable (not blocked, not parent, not already merged)
            # Should not be merged because last query will return events without parent
            # But if it's blocked, it should not be merged
            if event and event.mergeable:
                if self.parent is None:
                    self.parent = event
                    # Update parent modified date
                    self.parent.save()

    @hook(BEFORE_CREATE)
    @hook(BEFORE_UPDATE, when="network", has_changed=True)
    def network_assign(self):
        self.network = ngen.models.Network.objects.parent_of(self).first()

    @hook(AFTER_CREATE)
    def create_case(self):
        """Check if case should be created and create it"""
        if not self.parent:
            template = (
                CaseTemplate.objects.parents_of(self)
                .filter(event_taxonomy=self.taxonomy, event_feed=self.feed, active=True)
                .first()
            )
            if template:
                self.case = template.create_case(events=[self])

    @hook(AFTER_CREATE)
    @hook(AFTER_UPDATE, when="taxonomy", has_changed=True)
    def taxonomy_assign(self):
        self.todos.exclude(task__playbook__in=self.taxonomy.playbooks.all()).delete()
        for playbook in self.taxonomy.playbooks.all():
            for task in playbook.tasks.all():
                self.tasks.add(task)
        # Update taxonomy of children
        for child in self.children.all():
            child.taxonomy = self.taxonomy
            child.save()

    @hook(AFTER_CREATE)
    @hook(AFTER_UPDATE, when="case", has_changed=True, is_not=None)
    def case_assign_communication(self):
        # this will not be triggered if is event creation and case was created by
        # a CaseTemplate, because the case is created after the event and
        # self.case is None
        if self.case and self.case.state.attended and self.case.events.count() >= 1:
            self.case.communicate_v2("case_assign", events=[self])

    def clean(self):
        super().clean()
        self.update_taxonomy()
        if self.date and self.date > timezone.now():
            raise ValidationError(
                {"date": gettext_lazy("Date cannot be in the future")}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def merge(self, child: "Event", save_child: bool = True):
        super().merge(child, save_child)
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
            ngen.models.ArtifactRelation.objects.get_or_create(
                artifact=artifact_relation.artifact,
                object_id=self.id,
                content_type=ContentType.objects.get_for_model(self),
                defaults={"auto_created": False},
            )

    def email_contacts(self):
        contacts = []
        priority = (
            self.case.priority.severity
            if self.case.priority
            else self.priority.severity
        )
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

    def get_affected_contacts_extended(self):
        """
        Returns a list of dictionaries where the keys are the networks cidr or domain
        and the values are the contacts of the network.
        """
        priority = (
            self.case.priority.severity
            if self.case and self.case.priority
            else self.priority.severity
        )
        affected_networks = ngen.models.Network.objects.parent_of(self)[:1]

        network_contacts = []
        for network in affected_networks:
            network_cidr_or_domain = network.cidr if network.cidr else network.domain
            contacts = list(network.email_contacts(priority))
            if not contacts:
                contacts = list(network.ancestors_email_contacts(priority))
            network_contacts.append({network_cidr_or_domain: contacts})

        return network_contacts

    def get_affected_contacts(self):
        priority = (
            self.case.priority.severity
            if self.case and self.case.priority
            else self.priority.severity
        )
        affected_networks = ngen.models.Network.objects.parent_of(self)[:1]

        affected_contacts = []
        for network in affected_networks:
            network_contacts = list(network.email_contacts(priority))
            if not network_contacts:
                network_contacts = list(network.ancestors_email_contacts(priority))
            network_contact_emails = [
                contact.username
                for contact in network_contacts
                if contact.type == "email"
            ]
            affected_contacts.extend(network_contact_emails)

        return affected_contacts

    def get_reporter_contacts(self):
        return [self.reporter.email]

    def get_internal_contacts(self):
        return self.case.get_internal_contacts() if self.case else []

    def mark_as_solved(self, user=None, contact=None, contact_info=None):
        mark, _ = ngen.models.SolvedMark.objects.get_or_create(
            event=self,
            defaults={"user": user, "contact": contact, "contact_info": contact_info},
        )
        self.tags.add("solved")
        # update modified date
        self.save()
        return mark

    @staticmethod
    def export_events_to_zip(events):
        import shutil

        uniq_id = uuid.uuid4().hex[0:6]
        base_path = Path("/tmp")
        now = timezone.now().strftime("%Y%m%d_%H%M%S")
        export_dir = base_path / f"export_{now}_{uniq_id}"
        p = Path(export_dir)
        p.mkdir(parents=True, exist_ok=True)

        for event in events:
            event.export_event_to_directory(export_dir)

        # print all files and folders in export_dir
        for path in p.rglob("*"):
            print(path.relative_to(p))

        zip_filename = f"events_{now}_{uniq_id}.zip"
        zip_path = base_path / zip_filename

        shutil.make_archive(
            str(zip_path.with_suffix("")), "zip", root_dir=str(export_dir)
        )
        # shutil.rmtree(export_dir)
        return zip_path

    def export_event_to_directory(self, path):
        """
        Export a single event to a directory with the following structure:

        /path/event_<address>_<short_uuid>/
            event_report.html
            event_report.txt
            evidence/
                <evidence files>
        """

        base_path = Path(path)
        base_path.mkdir(parents=True, exist_ok=True)
        addr = lambda nombre: re.sub(r'[<>:"/\\|?*]', "_", nombre).strip() or "archivo"
        event_path = (
            base_path
            / f"event_{addr(self.address.address)[:50]}_{str(self.uuid).split('-')[0]}"
        )
        event_path.mkdir(parents=True, exist_ok=True)

        exported_template = Communication.render_template(
            "reports/case_report.html", extra_params=self.template_params
        )
        with open(event_path / "event_report.html", "w") as f:
            f.write(exported_template.get("html", ""))

        with open(event_path / "event_report.txt", "w") as f:
            f.write(exported_template.get("text", ""))

        # Export evidence files
        evidence_path = event_path / "evidence"
        evidence_path.mkdir(exist_ok=True)
        for evidence in self.evidence.all():
            evidence_file_path = evidence_path / evidence.attachment_name
            with open(evidence_file_path, "wb") as ef:
                ef.write(evidence.file.read())

        return event_path


class Evidence(AuditModelMixin, ValidationModelMixin):
    def directory_path(self, filename=None):
        return f"{self.get_related().evidence_path()}/{filename}"

    file = models.FileField(
        upload_to=directory_path,
        null=True,
        storage=HashedFilenameStorage(),
        unique=True,
    )
    object_id = models.PositiveIntegerField()
    assigned_name = models.CharField(max_length=100, null=True, blank=True, default="")
    original_filename = models.CharField(
        max_length=255, null=True, blank=True, default="", editable=False
    )
    size = models.PositiveIntegerField(default=0, editable=False)
    extension = models.CharField(
        max_length=255, null=True, blank=True, default="", editable=False
    )
    mime = models.CharField(
        max_length=255, null=True, blank=True, default="", editable=False
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey()

    class Meta:
        db_table = "evidence"
        permissions = [
            ("view_evidence_network_admin", "Can view evidence as network admin"),
            ("add_evidence_network_admin", "Can add evidence as network admin"),
            ("change_evidence_network_admin", "Can change evidence as network admin"),
            ("delete_evidence_network_admin", "Can delete evidence as network admin"),
        ]

    def get_related(self):
        return self.content_object

    def __str__(self):
        return self.file.url

    @property
    def attachment_name(self):
        return f'{self.get_related().__class__.__name__}({self.get_related().uuid})_{self.created.date()}_{self.assigned_name + "_" if self.assigned_name.strip() else ""}{self.filename}'

    @property
    def filename(self):
        return Path(self.file.name).name

    def delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)
        self.file.storage.delete(self.file.name)

    def save(self, *args, **kwargs):
        """
        Set assigned_name, size, extension, mime and original_filename fields.
        assigned_name:
            1. strip the assigned_name removing leading and trailing whitespaces
            2. split the assigned_name by '.' and get the first part
            3. remove any non-word characters [^a-zA-Z0-9_]
            4. replace '_' with '-'
        """
        if self.assigned_name:
            self.assigned_name = re.sub(
                r"[\W]+", "-", self.assigned_name.strip().split(".")[0]
            ).replace("_", "-")
        self.original_filename = self.file.name
        self.size = self.file.size
        self.extension = Path(self.file.name).suffix
        self.mime = get_mime_type(self.file.open("rb"))
        super().save(*args, **kwargs)


class CaseTemplate(
    AuditModelMixin, PriorityModelMixin, AddressModelMixin, ValidationModelMixin
):
    event_taxonomy = models.ForeignKey("ngen.Taxonomy", models.PROTECT)
    event_feed = models.ForeignKey("ngen.Feed", models.PROTECT)

    case_tlp = models.ForeignKey("ngen.Tlp", models.PROTECT)
    case_state = models.ForeignKey(
        "ngen.State", models.PROTECT, related_name="decision_states"
    )
    case_lifecycle = models.CharField(
        choices=LIFECYCLE, default=LIFECYCLE.auto, max_length=20
    )

    active = models.BooleanField(default=True)

    class Meta:
        db_table = "case_template"

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        qs = self.__class__.objects.filter(
            cidr=self.cidr,
            domain=self.domain,
            event_taxonomy=self.event_taxonomy,
            event_feed=self.event_feed,
        ).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError("CIDR, Domain, Taxonomy, Feed tuple must be unique")

    @property
    def event_cidr(self):
        return self.cidr

    @property
    def event_domain(self):
        return self.domain

    @property
    def case_priority(self) -> "Priority":
        return self.priority

    def create_case(self, events: list = []) -> "Case":
        return Case.objects.create(
            tlp=self.case_tlp,
            lifecycle=self.case_lifecycle,
            state=self.case_state,
            casetemplate_creator=self,
            events=events,
            priority=self.case_priority,
        )

    @property
    def matching_events_without_case_count(self):
        return self.get_matching_events_without_case().count()

    @matching_events_without_case_count.setter
    def matching_events_without_case_count(self, value):
        pass

    def get_matching_events_without_case(self):
        return Event.objects.children_of(self).filter(
            case__isnull=True,
            taxonomy=self.event_taxonomy,
            feed=self.event_feed,
            parent=None,
        )

    def create_cases_for_matching_events(self):
        return [
            self.create_case([event])
            for event in self.get_matching_events_without_case()
        ]

    def __str__(self):
        return str(self.id)


class SolvedMark(AuditModelMixin, ValidationModelMixin):
    event = models.ForeignKey("ngen.Event", models.CASCADE, related_name="solved_marks")
    contact_info = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Contact info of the contact if it's not a contact or an user",
    )
    contact = models.ForeignKey("ngen.Contact", models.CASCADE, null=True, blank=True)
    user = models.ForeignKey("ngen.User", models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "solved_mark"

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        if not self.contact and not self.user and not self.contact_info:
            raise ValidationError("Contact, User or Contact Info must be set")
