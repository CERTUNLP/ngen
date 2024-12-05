from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from model_utils import Choices

from ngen.models import Event
from ngen.models.common.mixins import (
    AuditModelMixin,
    ValidationModelMixin
)


class EventAnalysis(AuditModelMixin, ValidationModelMixin):
    date = models.DateTimeField(default=timezone.now)
    analyzer_type = models.CharField(max_length=255)
    vulnerable = models.BooleanField()
    result = models.TextField()
    target = models.CharField(max_length=255)
    scan_type = models.CharField(max_length=255)
    analyzer_url = models.CharField(max_length=255)
    event = models.ForeignKey(Event, related_name='analyses', on_delete=models.CASCADE)

    def __str__(self):
        return f"Analysis {self.id} for Event {self.event.id}"

    class Meta:
        db_table = "event_analysis"