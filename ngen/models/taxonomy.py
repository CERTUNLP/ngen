from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Value
from django.db.models.functions import Replace
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_bleach.models import BleachField
from model_utils import Choices

from ngen.models.common.mixins import (
    AuditModelMixin,
    TreeModelMixin,
    PriorityModelMixin,
    SlugModelMixin,
    ValidationModelMixin,
)


class Taxonomy(AuditModelMixin, TreeModelMixin, SlugModelMixin, ValidationModelMixin):
    TYPE = Choices(
        ("vulnerability", gettext_lazy("Vulnerability")),
        ("incident", gettext_lazy("Incident")),
        ("other", gettext_lazy("Other")),
    )
    type = models.CharField(choices=TYPE, max_length=20)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True, default="")
    group = models.ForeignKey(
        "ngen.TaxonomyGroup",
        on_delete=models.CASCADE,
        related_name="taxonomies",
        null=True,
        blank=True,
        default=None,
    )
    alias_of = models.ForeignKey(
        "ngen.Taxonomy",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="aliases",
    )
    needs_review = models.BooleanField(default=True)
    node_order_by = ["id"]

    def delete(self):
        if self.get_children():
            self.get_children().update(parent=self.parent)
        super(Taxonomy, self).delete()

    def __str__(self):
        if self.is_internal:
            return self.name
        return f"{self.group}({self.name})"

    @property
    def is_internal(self):
        return self.group is None

    @property
    def is_alias(self):
        return self.alias_of is not None

    def slugify(self):
        if self.is_internal:
            return super().slugify()
        return f"{self.group.slug}-{super().slugify()}"

    def get_ancestors_reports(self, flat=True):
        reports = self.get_ancestors_related(lambda obj: obj.reports.all())
        return [report for report_list in reports for report in report_list]
             #nuevo cambio#
    def get_matching_report(self, lang):
        rep = self.reports.filter(lang=lang)
        if rep.exists():
            return rep[:1]
        else:
            return [r for r in self.get_ancestors_reports() if r.lang == lang][:1]

    class Meta:
        db_table = "taxonomy"

    def save(self, *args, **kwargs):
        old_elem = None
        # Check if group and parent group are the same
        if self._state.adding:
            # force group to be the same as parent group
            if self.parent:
                self.group = self.parent.group
        else:
            # check if group and parent group are the same
            if self.parent and self.group != self.parent.group:
                raise ValidationError(
                    {
                        "group": gettext_lazy(
                            "Group must be the same as parent group and cannot be changed"
                        ),
                        "parent": gettext_lazy("Parent must be on the same group"),
                    }
                )
            # check if group is changing
            old_elem = self.__class__.objects.get(pk=self.pk)
            if self.group != old_elem.group:
                raise ValidationError({"group": gettext_lazy("Cannot change group")})

        if self.alias_of:
            if self.alias_of.alias_of:
                raise ValidationError(
                    {"alias_of": gettext_lazy("Cannot create an alias of an alias")}
                )

            if self.alias_of == self:
                raise ValidationError(
                    {"alias_of": gettext_lazy("Cannot create an alias of itself")}
                )

            if not self.alias_of.is_internal:
                raise ValidationError(
                    {
                        "alias_of": gettext_lazy(
                            "Only internal taxonomies can be aliased"
                        )
                    }
                )

            if self.parent and self.is_internal:
                raise ValidationError(
                    {
                        "alias_of": gettext_lazy(
                            "Internal taxonomy with parent cannot have alias"
                        ),
                        "parent": gettext_lazy(
                            "Internal taxonomy alias cannot have parent"
                        ),
                    }
                )

            if not self._state.adding:
                old_elem = old_elem or self.__class__.objects.get(pk=self.pk)
                original_alias_of = old_elem.alias_of
                if original_alias_of != self.alias_of:
                    self.events.update(taxonomy=self.alias_of)

        if not self.type:
            if self.alias_of:
                self.type = self.alias_of.type
            elif self.parent:
                self.type = self.parent.type
            else:
                self.type = Taxonomy.TYPE.other

        super().save(*args, **kwargs)


class TaxonomyGroup(AuditModelMixin, SlugModelMixin, ValidationModelMixin):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True, default="")
    node_order_by = ["id"]
    needs_review = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "taxonomy_group"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        # Only one internal and one alias taxonomy group is allowed
        # Cannot change the name of an internal or alias taxonomy group
        original_slug = ""
        if not self._state.adding:
            original_slug = TaxonomyGroup.objects.get(pk=self.pk).slug
        super().save(*args, **kwargs)
        # if not adding and original_name != self.name update all taxonomy slug with the new group name
        if not self._state.adding and original_slug != self.slug:
            Taxonomy.objects.filter(group=self).update(
                slug=Replace("slug", Value(f"{original_slug}-"), Value(f"{self.slug}-"))
            )


class Report(AuditModelMixin, ValidationModelMixin):
    LANG = Choices("en", "es")
    lang = models.CharField(choices=LANG, default=LANG.en, max_length=2)
    taxonomy = models.ForeignKey(
        "ngen.Taxonomy", models.CASCADE, related_name="reports"
    )
    problem = BleachField()
    derived_problem = BleachField(null=True, blank=True)
    verification = BleachField(null=True, blank=True)
    recommendations = BleachField(null=True, blank=True)
    more_information = BleachField(null=True, blank=True)

    class Meta:
        db_table = "report"
        unique_together = ["lang", "taxonomy"]

    def __str__(self):
        return "%s (%s)" % (self.taxonomy.name, self.lang)


class Playbook(AuditModelMixin, ValidationModelMixin):
    name = models.CharField(max_length=60)
    taxonomy = models.ManyToManyField("Taxonomy", related_name="playbooks")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "playbook"
        ordering = ["name"]


class Task(AuditModelMixin, PriorityModelMixin, ValidationModelMixin):
    name = models.CharField(max_length=140)
    playbook = models.ForeignKey(
        "ngen.Playbook", on_delete=models.CASCADE, related_name="tasks"
    )
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "task"
        ordering = ["priority__severity"]


class TodoTask(AuditModelMixin, ValidationModelMixin):
    task = models.ForeignKey(
        "ngen.Task", on_delete=models.CASCADE, related_name="todos"
    )
    event = models.ForeignKey(
        "ngen.Event", on_delete=models.CASCADE, related_name="todos"
    )
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True)
    note = models.TextField(null=True)
    assigned_to = models.ForeignKey(
        "ngen.User", null=True, related_name="assigned_tasks", on_delete=models.PROTECT
    )

    def save(self, **kwargs):
        if self.completed:
            self.completed_date = timezone.now()
        super().save()

    class Meta:
        db_table = "todo_task"
        ordering = ["task__playbook"]
        unique_together = ["task", "event"]
