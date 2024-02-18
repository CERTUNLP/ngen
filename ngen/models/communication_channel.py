from django.db import models
from ngen.models.common.mixins import AuditModelMixin
from ngen.models import CanalizableMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from model_utils import Choices


class CommunicationChannel(AuditModelMixin):
    """
    CommunicationChannel model
    """

    name = models.CharField(blank=False, max_length=255)
    message_id = models.CharField(max_length=255, null=True, blank=True, default=None)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    canalizable = GenericForeignKey("content_type", "object_id")

    def communication_types(self):
        """
        Method to get communication types
        """

        return CommunicationType.objects.filter(
            communication_channel_type_relations__communication_channel=self
        )

    def fetch_contacts(self):
        """
        Method to fetch contacts of every communication type
        """
        contacts_by_type = {}
        for communication_type in self.communication_types():
            contacts_dict = communication_type.get_contacts(self.canalizable)
            contacts_by_type[communication_type.type] = contacts_dict

        return contacts_by_type


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

    def get_contacts(self, canalizable_mixin: CanalizableMixin):
        """
        Method to get contacts
        """
        get_contacts_method = self.get_contacts_method()

        return get_contacts_method(canalizable_mixin)

    def get_contacts_method(self):
        """
        Method to get communication type method, based on the type
        """
        type_method_mapper = {
            CommunicationType.TYPE_CHOICES.affected: self.get_affected_contacts,
            CommunicationType.TYPE_CHOICES.reporter: self.get_reporter_contacts,
            CommunicationType.TYPE_CHOICES.intern: self.get_internal_contacts,
        }
        method = type_method_mapper.get(self.type)

        if method:
            return method

        raise ValueError(f"Method for Type: '{self.type}' not implemented")

    def get_affected_contacts(self, canalizable_mixin: CanalizableMixin):
        """
        Method to get affected contacts
        """
        return canalizable_mixin.get_affected_contacts()

    def get_reporter_contacts(self, canalizable_mixin: CanalizableMixin):
        """
        Method to get reporter contacts
        """
        return canalizable_mixin.get_reporter_contacts()

    def get_internal_contacts(self, canalizable_mixin: CanalizableMixin):
        """
        Method to get internal contacts
        """
        return canalizable_mixin.get_internal_contacts()


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
