from django.db import models
from django.utils.translation import gettext_lazy
from django.core.validators import RegexValidator
from taggit.models import TagBase, GenericTaggedItemBase

# Validador para asegurar que el color sea un código hexadecimal válido
hex_color_validator = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message=gettext_lazy("Color must be a valid hexadecimal code (e.g. #007bff)"),
)


class Tag(TagBase):
    color = models.CharField(
        max_length=7, default="#007bff", validators=[hex_color_validator]
    )

    class Meta:
        verbose_name = gettext_lazy("CustomTag")
        verbose_name_plural = gettext_lazy("CustomTags")

    def slugify(self, tag, i=None):
        return super().slugify(tag, i).replace("-", "_")


class TaggedObject(GenericTaggedItemBase):
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_items"
    )
