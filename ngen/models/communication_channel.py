from typing import Optional
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from model_utils import Choices

from ngen.mailer.email_handler import EmailHandler
from ngen.models import ChannelableMixin, AuditModelMixin
from ngen.models.email_message import EmailMessage


class CommunicationType(AuditModelMixin):
    """
    CommunicationType model
    """

    TYPE_CHOICES = Choices(
        ("affected", "Affected"), ("reporter", "Reporter"), ("intern", "Intern")
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=255)

    def save(self, *args, **kwargs):
        if self.type not in self.TYPE_CHOICES:
            type_choices = ", ".join([choice[1] for choice in self.TYPE_CHOICES])
            raise ValidationError(f"Invalid type. Valid options are {type_choices}")
        super().save(*args, **kwargs)

    def get_contacts(self, channelable_mixin: ChannelableMixin):
        """
        Method to get contacts
        """
        get_contacts_method = self.get_contacts_method()

        return get_contacts_method(channelable_mixin)

    def get_contacts_method(self):
        """
        Method to get communication type method, based on the type
        """
        type_method_mapper = {
            CommunicationType.TYPE_CHOICES.affected: self.get_affected_contacts,
            CommunicationType.TYPE_CHOICES.reporter: self.get_reporter_contacts,
            CommunicationType.TYPE_CHOICES.intern: self.get_team_and_assigned_contacts,
        }
        method = type_method_mapper.get(self.type)

        if method:
            return method

        raise ValueError(f"Method for Type: '{self.type}' not implemented")

    def get_affected_contacts(self, channelable_mixin: ChannelableMixin):
        """
        Method to get affected contacts
        """
        return channelable_mixin.get_affected_contacts()

    def get_reporter_contacts(self, channelable_mixin: ChannelableMixin):
        """
        Method to get reporter contacts
        """
        return channelable_mixin.get_reporter_contacts()

    def get_team_and_assigned_contacts(self, channelable_mixin: ChannelableMixin):
        """
        Method to get internal contacts.
        """
        return channelable_mixin.get_team_and_assigned_contacts()


class CommunicationChannel(AuditModelMixin):
    """
    CommunicationChannel model
    """

    name = models.CharField(blank=False, max_length=255)
    message_id = models.CharField(max_length=255, null=True, blank=True, default=None)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    channelable = GenericForeignKey("content_type", "object_id")

    communication_types = models.ManyToManyField(
        CommunicationType, through="CommunicationChannelTypeRelation"
    )

    additional_contacts = models.JSONField(default=list, null=True, blank=True)

    @classmethod
    def create_custom_channel(
        cls,
        channelable=None,
        channel_name: str = None,
        channel_type: list = None,
        additional_contacts=None,
    ):
        """
        Method to create a communication channel of any type
        """
        if not channel_type:
            raise ValueError("At least one channel type is required")

        communication_channel = cls.objects.create(
            name=channel_name,
            channelable=channelable,
            additional_contacts=additional_contacts or [],
        )
        communication_types = [
            CommunicationType.objects.get_or_create(type=type)[0]
            for type in channel_type
        ]
        communication_channel.communication_types.add(*communication_types)

        return communication_channel

    @classmethod
    def get_or_create_custom_channel(
        cls,
        channelable=None,
        channel_name: str = None,
        channel_type: list = None,
        additional_contacts=None,
    ):
        """
        Method to get or create a communication channel of any type
        """
        if not channelable:
            raise ValueError("Channelable is required")

        if not channel_type:
            raise ValueError("At least one channel type is required")

        existing_channel = channelable.communication_channels.filter(
            communication_types__type__in=channel_type
        ).first()

        if existing_channel:
            return existing_channel

        return cls.create_custom_channel(
            channelable=channelable,
            channel_name=channel_name,
            channel_type=channel_type,
            additional_contacts=additional_contacts,
        )

    @classmethod
    def create_channel_with_affected(
        cls, channelable=None, channel_name=None, additional_contacts=None
    ):
        """
        Method to create a communication channel with affected contacts
        """
        return cls.create_custom_channel(
            channelable=channelable,
            channel_name=channel_name or "Affected Communication Channel",
            channel_type=[CommunicationType.TYPE_CHOICES.affected],
            additional_contacts=additional_contacts,
        )

    @classmethod
    def create_channel_with_intern(
        cls, channelable=None, channel_name=None, additional_contacts=None
    ):
        """
        Method to create a communication channel with intern contacts
        """
        return cls.create_custom_channel(
            channelable=channelable,
            channel_name=channel_name or "Intern Communication Channel",
            channel_type=[CommunicationType.TYPE_CHOICES.intern],
            additional_contacts=additional_contacts,
        )

    @classmethod
    def create_channel_with_reporter(
        cls, channelable=None, channel_name=None, additional_contacts=None
    ):
        """
        Method to create a communication channel with reporter contacts
        """
        return cls.create_custom_channel(
            channelable=channelable,
            channel_name=channel_name or "Reporter Communication Channel",
            channel_type=[CommunicationType.TYPE_CHOICES.reporter],
            additional_contacts=additional_contacts,
        )

    @classmethod
    def get_or_create_channel_with_affected(
        cls, channelable=None, channel_name=None, additional_contacts=None
    ):
        """
        Method to get or create a communication channel with affected contacts
        """
        return cls.get_or_create_custom_channel(
            channelable=channelable,
            channel_name=channel_name or "Affected Communication Channel",
            channel_type=[CommunicationType.TYPE_CHOICES.affected],
            additional_contacts=additional_contacts,
        )

    @classmethod
    def get_or_create_channel_with_intern(
        cls, channelable=None, channel_name=None, additional_contacts=None
    ):
        """
        Method to get or create a communication channel with intern contacts
        """
        return cls.get_or_create_custom_channel(
            channelable=channelable,
            channel_name=channel_name or "Intern Communication Channel",
            channel_type=[CommunicationType.TYPE_CHOICES.intern],
            additional_contacts=additional_contacts,
        )

    @classmethod
    def get_or_create_channel_with_reporter(
        cls, channelable=None, channel_name=None, additional_contacts=None
    ):
        """
        Method to get or create a communication channel with reporter contacts
        """
        return cls.get_or_create_custom_channel(
            channelable=channelable,
            channel_name=channel_name or "Reporter Communication Channel",
            channel_type=[CommunicationType.TYPE_CHOICES.reporter],
            additional_contacts=additional_contacts,
        )

    def fetch_contacts(self):
        """
        Method to fetch contacts of every communication type
        """
        contacts_by_type = {}
        for communication_type in self.communication_types.all():
            contacts_dict = communication_type.get_contacts(self.channelable)
            contacts_by_type[communication_type.type] = contacts_dict

        return contacts_by_type

    def fetch_contact_emails(self):
        """
        Method to fetch emails of every contact
        """
        contacts = self.fetch_contacts()

        contact_emails = [
            email for email_list in contacts.values() for email in email_list
        ]

        if self.additional_contacts:
            contact_emails += self.additional_contacts

        return contact_emails

    def get_messages(self):
        """
        Get all messages sent in the channel
        """
        if not self.message_id:
            return None

        return EmailMessage.get_message_thread_by(self.message_id)

    def get_last_message(self):
        """
        Get the last message sent in the channel
        """
        messages = self.get_messages()
        return messages.last() if messages else None

    def communicate(
        self,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        template: Optional[str] = None,
        template_params: Optional[dict] = None,
        bcc_recipients: Optional[list] = None,
        attachments: Optional[list] = None,
    ):
        """
        Method to send an email in a communication channel.
        If the channel has no message_id, the message id of the sent email
        will be set in the channel. If the channel has a message_id, the sent email
        will be a reply to the last message sent in the channel.
        """
        if not body and not template:
            raise ValueError("Body or template is required")

        email_handler = EmailHandler()

        sent_email = email_handler.send_email(
            recipients=self.fetch_contact_emails(),
            bcc_recipients=bcc_recipients,
            subject=subject or "-",
            body=body,
            template=template,
            template_params=template_params,
            in_reply_to=self.get_last_message() if self.message_id else None,
            attachments=attachments,
        )

        if not self.message_id:
            self.message_id = sent_email.message_id
            self.save()

        return sent_email


class CommunicationChannelTypeRelation(AuditModelMixin):
    """
    CommunicationChannelTypeRelation model, represents the many-to-many relationship
    between a Communication Channel and a Communication Type
    """

    communication_channel = models.ForeignKey(
        CommunicationChannel,
        on_delete=models.CASCADE,
        related_name="communication_channel_type_relations",
    )

    communication_type = models.ForeignKey(
        CommunicationType,
        on_delete=models.CASCADE,
        related_name="communication_channel_type_relations",
    )

    class Meta:
        """
        Unique tuples for communication channel and communication type
        """

        unique_together = ["communication_channel", "communication_type"]
