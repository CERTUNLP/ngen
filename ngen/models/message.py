from django.db import models

from ngen.models.common.mixins import AuditModelMixin, ValidationModelMixin


class Message(AuditModelMixin, ValidationModelMixin):
    data = models.JSONField()
    response = models.JSONField(blank=True, null=True)
    pending = models.IntegerField()
    case = models.ForeignKey('ngen.Case', models.PROTECT, blank=True, null=True)
    discr = models.CharField(max_length=255)
    created_by = models.ForeignKey('ngen.User', models.PROTECT, blank=True, null=True)

    class Meta:
        db_table = 'message'
