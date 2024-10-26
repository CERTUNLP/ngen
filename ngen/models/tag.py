from django.db import models
from django.utils.translation import gettext_lazy
from taggit.models import TagBase, GenericTaggedItemBase


class Tag(TagBase):
    color = models.CharField(max_length=7, default="#007bff")

    class Meta:
        verbose_name = gettext_lazy("Tag")
        verbose_name_plural = gettext_lazy("Tags")


class TaggedObject(GenericTaggedItemBase):
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_items"
    )
