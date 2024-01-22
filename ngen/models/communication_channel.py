from typing import List
from django.db import models
from ngen.models.common.mixins import AuditModelMixin
from ngen.models import CanalizableMixin
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from model_utils import Choices


class CommunicationChannel(AuditModelMixin):
    """
    CommunicationChannel model
    """

    name = models.CharField(blank=False, max_length=255)
    message_id = models.IntegerField()

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
        contacts = []
        for communication_type in self.communication_types():
            contacts += communication_type.get_contacts(self.canalizable)
        return contacts


class CommunicationType(AuditModelMixin):
    """
    CommunicationType model
    """

    name = models.CharField(blank=False, max_length=255)
    TYPE_CHOICES = Choices(
        ("affected", "Affected"), ("reporter", "Reporter"), ("intern", "Intern")
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=255)
    communication_channel_type_relation = GenericRelation(
        "ngen.CommunicationChannelTypeRelation",
        related_name="communication_channel_type_relation",
    )

    TYPE_METHOD_MAPPER = {
        TYPE_CHOICES.affected: "get_affected_contacts",
        TYPE_CHOICES.reporter: "get_reporter_contacts",
        TYPE_CHOICES.intern: "get_internal_contacts",
    }

    def get_contacts(self, canalizable_mixin: CanalizableMixin):
        """
        Method to get contacts
        """
        method_name = self.TYPE_METHOD_MAPPER[self.type]
        get_contacts_method = getattr(self, method_name)

        if get_contacts_method and callable(get_contacts_method):
            return get_contacts_method(canalizable_mixin)
        else:
            raise ValueError(f"Unknown method: {method_name}")

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
