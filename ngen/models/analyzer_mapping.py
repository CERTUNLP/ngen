from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from model_utils import Choices

from ngen.models import Taxonomy
from ngen.models.common.mixins import (
    AuditModelMixin,
    ValidationModelMixin
)


class AnalyzerMapping(AuditModelMixin, ValidationModelMixin):
    date = models.DateTimeField(default=timezone.now)
    mapping_from = models.ForeignKey(Taxonomy, related_name='mappings', on_delete=models.CASCADE)
    mapping_to = models.CharField(max_length=255)
    analyzer_type = models.CharField(max_length=255)

    def __str__(self):
        return f"Mapping {self.id} for Taxonomy {self.mapping_from.id}"

    class Meta:
        db_table = "analyzer_mapping"