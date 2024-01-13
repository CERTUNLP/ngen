from typing import List
from django.db import models
from ngen.models.common.mixins import AuditModelMixin
from ngen.models import Contact, CanalizableMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class CommunicationType(AuditModelMixin):
    """
    CommunicationType abstract model
    """

    name = models.CharField(blank=False, max_length=255)

    class Meta:
        abstract = True

    def get_contacts(self, canalizable_mixin: CanalizableMixin) -> List[Contact]:
        """
        Method to get contacts
        """
        raise NotImplementedError


class InternCommunicationType(CommunicationType):
    """
    InternCommunicationType model
    """

    def get_contacts(self, canalizable_mixin: CanalizableMixin) -> List[Contact]:
        return canalizable_mixin.get_internal_contacts()


class AffectedCommunicationType(CommunicationType):
    """
    AffectedCommunicationType model
    """

    def get_contacts(self, canalizable_mixin: CanalizableMixin) -> List[Contact]:
        return canalizable_mixin.get_affected_contacts()


class ReporterCommunicationType(CommunicationType):
    """
    ReporterCommunicationType model
    """

    def get_contacts(self, canalizable_mixin: CanalizableMixin) -> List[Contact]:
        return canalizable_mixin.get_reporter_contacts()


class CommunicationChannel(AuditModelMixin):
    """
    CommunicationChannel model
    """

    name = models.CharField(blank=False, max_length=255)
    message_id = models.IntegerField()

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="communication_channel"
    )
    object_id = models.PositiveIntegerField()
    canalizable = GenericForeignKey("content_type", "object_id")

    def fetch_contacts(self):
        """
        Method to fetch contacts
        """


class CommunicationChannelTypeRelation(AuditModelMixin):
    """
    CommunicationTypeRelation model, represents the many-to-many relationship
    between a communication channel and a communication type
    """

    communication_channel = models.ForeignKey(
        CommunicationChannel,
        on_delete=models.CASCADE,
        related_name="communication_type_relations",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="communication_type_relations",
    )
    object_id = models.PositiveIntegerField()
    communication_type = GenericForeignKey("content_type", "object_id")

    class Meta:
        """
        Unique tuples for communication channel and communication type
        """

        unique_together = ["communication_channel", "content_type", "object_id"]
