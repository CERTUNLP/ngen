from django.db import models
from django_bleach.models import BleachField
from model_utils import Choices

from .utils import NgenModel, NgenEvidenceMixin, NgenPriorityMixin
from ..communication import Communication


class Announcement(NgenModel, NgenPriorityMixin, NgenEvidenceMixin, Communication):
    title = models.CharField(max_length=255)
    body = BleachField(null=True)
    LANG = Choices('en', 'es')
    lang = models.CharField(choices=LANG, default=LANG.en, max_length=2)
    tlp = models.ForeignKey('ngen.Tlp', models.DO_NOTHING)
    network = models.ForeignKey('ngen.Network', models.DO_NOTHING)

    class Meta:
        db_table = 'announcement'

    def save(self, *args, **kwargs):
        super(Announcement, self).save()
        self.communicate(self.title, 'reports/announcement_base.html')

    @property
    def recipients(self) -> dict[str, list]:
        recipients = super(Announcement, self).recipients
        event_contacts = list(self.network.email_contacts(self.priority.severity))
        if event_contacts:
            recipients.update({'to': [c.username for c in event_contacts]})
        else:
            network_contacts = self.network.ancestors_email_contacts(self.priority.severity)
            if network_contacts:
                recipients.update({'to': [network_contacts[0]]})
        return recipients

    @property
    def template_params(self) -> dict:
        return {'tlp': self.tlp, 'priority': self.priority, 'body': self.body}

    @property
    def email_attachments(self) -> list[dict]:
        attachments = []
        for evidence in self.evidence.all():
            attachments.append({'name': evidence.attachment_name, 'file': evidence.file})
        return attachments
