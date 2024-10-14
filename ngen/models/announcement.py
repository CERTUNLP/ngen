import re
import logging
from collections import defaultdict

from constance import config
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import get_template
from django.utils.html import strip_tags
from django_bleach.models import BleachField
from model_utils import Choices

from ngen.models.common.mixins import (
    AuditModelMixin,
    EvidenceModelMixin,
    PriorityModelMixin,
    ValidationModelMixin,
)

logger = logging.getLogger(__name__)


class Communication:
    @staticmethod
    def send_mail(
        subject,
        content: dict,
        recipients: dict[str, list],
        attachments: list[dict] = None,
        extra_headers: dict = None,
    ):
        if recipients["to"]:
            email = EmailMultiAlternatives(
                subject,
                content["text"],
                recipients["from"],
                recipients["to"],
                bcc=recipients["bcc"],
                cc=recipients["cc"],
            )
            email.attach_alternative(content["html"], "text/html")
            email.extra_headers.update(extra_headers)
            for attachment in attachments:
                try:
                    email.attach(attachment["name"], attachment["file"].read())
                except Exception as e:
                    logger.error(f"Error attaching file: {e}")
            email.send()

    @staticmethod
    def render_template(
        template: str, extra_params: dict = None, lang: str = None
    ) -> dict:
        content = {}
        lang = lang if lang else config.NGEN_LANG
        params = {"lang": lang, "config": config}
        if extra_params:
            params.update(extra_params)
        content["text"] = re.sub(
            r"\n+",
            "\n",
            strip_tags(get_template(template).render(params)).replace("  ", ""),
        )
        params.update({"html": True})
        content["html"] = get_template(template).render(params)
        return content

    def communicate(self, title: str, template: str, **kwargs):
        # DEPRECATED: Use send_mail instead
        return self.send_mail(
            self.subject(title),
            self.render_template(template, extra_params=self.template_params),
            self.recipients,
            self.email_attachments,
            self.email_headers,
        )

    def subject(self, title: str = None) -> str:
        return title

    @property
    def recipients(self) -> dict[str, list]:
        recipients = defaultdict(list)
        recipients["from"] = config.EMAIL_SENDER
        return recipients

    @property
    def template_params(self) -> dict:
        raise NotImplementedError

    @property
    def email_headers(self) -> dict:
        return {}

    @property
    def email_attachments(self) -> list[dict]:
        raise NotImplementedError


class Announcement(
    AuditModelMixin,
    PriorityModelMixin,
    EvidenceModelMixin,
    Communication,
    ValidationModelMixin,
):
    title = models.CharField(max_length=255)
    body = BleachField(null=True)
    LANG = Choices("en", "es")
    lang = models.CharField(choices=LANG, default=LANG.en, max_length=2)
    tlp = models.ForeignKey("ngen.Tlp", models.PROTECT)
    network = models.ForeignKey("ngen.Network", models.PROTECT)

    class Meta:
        db_table = "announcement"

    def save(self, *args, **kwargs):
        super(Announcement, self).save()
        self.communicate(self.title, "reports/announcement_base.html")

    @property
    def recipients(self) -> dict[str, list]:
        recipients = super(Announcement, self).recipients
        event_contacts = list(self.network.email_contacts(self.priority.severity))
        if event_contacts:
            recipients.update({"to": [c.username for c in event_contacts]})
        else:
            network_contacts = self.network.ancestors_email_contacts(
                self.priority.severity
            )
            if network_contacts:
                recipients.update({"to": [network_contacts[0]]})
        return recipients

    @property
    def template_params(self) -> dict:
        return {"tlp": self.tlp, "priority": self.priority, "body": self.body}

    @property
    def email_attachments(self) -> list[dict]:
        attachments = []
        for evidence in self.evidence.all():
            attachments.append(
                {"name": evidence.attachment_name, "file": evidence.file}
            )
        return attachments
