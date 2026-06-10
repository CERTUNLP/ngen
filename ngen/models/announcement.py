import re
import logging
from collections import defaultdict
from django.db import models
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.translation import gettext
from django_bleach.models import BleachField
from model_utils import Choices
from constance import config

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
        attachments = attachments or []
        extra_headers = extra_headers or {}
        if not recipients.get("to") and not recipients.get("cc") and not recipients.get("bcc"):
            logger.warning(
                "Communication.send_mail: skipped (no recipients) subject='%s'", subject
            )
            return

        email_message = Communication._build_email_message(
            subject, content, recipients, attachments
        )

        if config.EMAIL_AUTO_SEND:
            Communication._dispatch_to_celery(email_message)
        else:
            logger.info(
                "Communication.send_mail: stored id=%s (EMAIL_AUTO_SEND=false) subject='%s' to=%s",
                email_message.id,
                subject,
                recipients.get("to", []),
            )

    @staticmethod
    def _build_email_message(subject, content, recipients, attachments):
        from ngen.models.email_message import EmailMessage as EmailMessageModel
        from django.conf import settings
        from os import path, makedirs
        from shutil import copyfileobj

        message_id = EmailMessageModel.generate_message_id(
            domain=config.EMAIL_SENDER.split("@")[1] if config.EMAIL_SENDER and "@" in config.EMAIL_SENDER else "localhost"
        )

        def _format_recipients(email_list):
            formatted = []
            if not email_list:
                return formatted
            for email in email_list:
                if isinstance(email, str):
                    formatted.append({"name": email.split("@")[0], "email": email})
                elif isinstance(email, dict):
                    formatted.append(email)
            return formatted

        sender_name = config.EMAIL_USERNAME or config.EMAIL_SENDER.split("@")[0] if config.EMAIL_SENDER else ""
        senders = [{"name": sender_name, "email": config.EMAIL_SENDER}]

        email_recipients = _format_recipients(recipients.get("to", []))
        email_cc = _format_recipients(recipients.get("cc", []))
        email_bcc = _format_recipients(recipients.get("bcc", []))

        saved_attachments = []
        if attachments:
            attachments_dir = path.join(
                settings.MEDIA_ROOT,
                settings.EMAIL_ATTACHMENTS_FILE_ROOT,
                message_id,
            )
            makedirs(attachments_dir, exist_ok=True)
            for att in attachments:
                filename = path.basename(att.get("name", "attachment"))
                filepath = path.join(attachments_dir, filename)
                with open(filepath, "wb") as dest:
                    copyfileobj(att["file"], dest)
                saved_attachments.append({
                    "name": filename,
                    "file": path.join(settings.EMAIL_ATTACHMENTS_FILE_ROOT, message_id, filename),
                })

        email_message = EmailMessageModel.objects.create(
            root_message_id=message_id,
            message_id=message_id,
            senders=senders,
            recipients=email_recipients + email_cc,
            bcc_recipients=email_bcc,
            subject=subject,
            body=content.get("text", ""),
            body_html=content.get("html", ""),
            template=content.get("template", None),
            attachments=saved_attachments,
        )

        logger.info(
            "Communication._build_email_message: created id=%s subject='%s' to=%s cc=%s bcc=%s attachments=%s",
            email_message.id,
            subject,
            [r["email"] for r in email_recipients],
            [r["email"] for r in email_cc],
            [r["email"] for r in email_bcc],
            len(saved_attachments),
        )

        return email_message

    @staticmethod
    def _dispatch_to_celery(email_message):
        from ngen.tasks import async_send_email

        async_send_email.delay(email_message.id)
        email_message.dispatched = True
        email_message.save(update_fields=["dispatched"])

        logger.info(
            "Communication._dispatch_to_celery: dispatched id=%s subject='%s' to=%s",
            email_message.id,
            email_message.subject,
            [r["email"] for r in email_message.recipients],
        )

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
        html = re.sub(r"\s+", " ", get_template(template).render(params)).strip()
        content["html"] = html

        return content

    def communicate(self, title: str, template: str, **kwargs):
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

    @staticmethod
    def communicate_contact_summary(contact, open_cases, closed_cases, tlp, days):
        """
        Weekly cases summary communication
        """
        subject = "[%s][TLP:%s] %s" % (
            config.TEAM_NAME,
            tlp.name.upper(),
            gettext("Summary"),
        )
        template = "reports/summary_contact.html"
        Communication.send_mail(
            subject,
            Communication.render_template(
                template,
                extra_params={
                    "contact": contact,
                    "open_cases": open_cases,
                    "closed_cases": closed_cases,
                    "tlp": tlp,
                    "days": days,
                    "full_summary_report_link": config.FULL_SUMMARY_REPORT_LINK,
                },
            ),
            {
                "to": [contact.username],
                "from": config.EMAIL_SENDER,
                "bcc": [config.TEAM_EMAIL],
            },
        )

    @staticmethod
    def communicate_contact_summary_export(
        contact, open_cases, closed_cases, tlp, days, attachments=[]
    ):
        """
        Weekly cases summary communication with exported attachments
        """
        subject = "[%s][TLP:%s] %s" % (
            config.TEAM_NAME,
            tlp.name.upper(),
            gettext("Full Summary"),
        )
        template = "reports/summary_contact.html"
        Communication.send_mail(
            subject,
            Communication.render_template(
                template,
                extra_params={
                    "contact": contact,
                    "open_cases": open_cases,
                    "closed_cases": closed_cases,
                    "tlp": tlp,
                    "days": days,
                },
            ),
            {
                "to": [contact.username],
                "from": config.EMAIL_SENDER,
                "bcc": [config.TEAM_EMAIL],
            },
            attachments=attachments,
        )

    @staticmethod
    def send_contact_check_email(contact, networks, check):
        """
        Sends an email to the contact to validate their information.
        """
        subject = "[%s] %s" % (
            config.TEAM_NAME,
            gettext("Contact verification"),
        )

        template = "reports/contact_check.html"

        Communication.send_mail(
            subject,
            Communication.render_template(
                template,
                extra_params={
                    "contact": contact,
                    "networks": networks,
                    "check": check,
                },
            ),
            {
                "to": [contact.username],
                "from": config.EMAIL_SENDER,
                "bcc": [config.TEAM_EMAIL],
            },
        )

    @staticmethod
    def send_contact_check_submitted(contact, networks, check):
        """
        Sends an email to the team when a contact completes the verification form.
        """
        subject = "[%s] %s" % (
            config.TEAM_NAME,
            gettext("Contact check submitted"),
        )

        template = "reports/contact_check_submitted.html"

        Communication.send_mail(
            subject,
            Communication.render_template(
                template,
                extra_params={
                    "contact": contact,
                    "networks": networks,
                    "check": check,
                },
            ),
            {
                "to": [config.TEAM_EMAIL],
                "from": config.EMAIL_SENDER,
            },
        )


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
