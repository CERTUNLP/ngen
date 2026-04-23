from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy

from ngen.models.common.mixins import AuditModelMixin, ValidationModelMixin


class Analyzer(AuditModelMixin, ValidationModelMixin):
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=50)
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "analyzer"

    def __str__(self):
        return self.name

    def clean_fields(self, exclude=None):
        from ngen.analyzers.registry import ADAPTER_REGISTRY

        if self.type and self.type not in ADAPTER_REGISTRY:
            valid = ", ".join(ADAPTER_REGISTRY.keys())
            raise ValidationError(
                {"type": gettext_lazy(f"Invalid type. Valid choices: {valid}")}
            )
        super().clean_fields(exclude=exclude)

    def clean(self):
        from ngen.analyzers.registry import ADAPTER_REGISTRY

        if self.type in ADAPTER_REGISTRY:
            adapter_class = ADAPTER_REGISTRY[self.type]
            instance = adapter_class(self)
            errors = instance.validate_config()
            if errors:
                raise ValidationError({"config": list(errors.values())})

    def get_adapter(self):
        from ngen.analyzers.registry import get_adapter

        return get_adapter(self)