from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_bleach.models import BleachField
from model_utils import Choices

from ngen.models.common.mixins import AuditModelMixin, TreeModelMixin, PriorityModelMixin, SlugModelMixin, \
    ValidationModelMixin


class Taxonomy(AuditModelMixin, TreeModelMixin, SlugModelMixin, ValidationModelMixin):
    TYPE = Choices(('vulnerability', gettext_lazy('Vulnerability')), ('incident', gettext_lazy('Incident')))
    type = models.CharField(choices=TYPE, max_length=20)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True, default='')
    node_order_by = ['id']

    def delete(self):
        if self.get_children():
            self.get_children().update(parent=self.parent)
        super(Taxonomy, self).delete()

    def __str__(self):
        return self.name

    def get_ancestors_reports(self):
        return self.get_ancestors_related(lambda obj: obj.reports.all())

    class Meta:
        db_table = 'taxonomy'


class Report(AuditModelMixin, ValidationModelMixin):
    LANG = Choices('en', 'es')
    lang = models.CharField(choices=LANG, default=LANG.en, max_length=2)
    taxonomy = models.ForeignKey('ngen.Taxonomy', models.CASCADE, related_name='reports')
    problem = BleachField()
    derived_problem = BleachField(null=True, blank=True)
    verification = BleachField(null=True, blank=True)
    recommendations = BleachField(null=True, blank=True)
    more_information = BleachField(null=True, blank=True)

    class Meta:
        db_table = 'report'
        unique_together = ['lang', 'taxonomy']

    def __str__(self):
        return "%s (%s)" % (self.taxonomy.name, self.lang)


class Playbook(AuditModelMixin, ValidationModelMixin):
    name = models.CharField(max_length=60)
    taxonomy = models.ManyToManyField('Taxonomy', related_name='playbooks')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'playbook'
        ordering = ["name"]


class Task(AuditModelMixin, PriorityModelMixin, ValidationModelMixin):
    name = models.CharField(max_length=140)
    playbook = models.ForeignKey('ngen.Playbook', on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'task'
        ordering = ["priority__severity"]


class TodoTask(AuditModelMixin, ValidationModelMixin):
    task = models.ForeignKey('ngen.Task', on_delete=models.CASCADE, related_name='todos')
    event = models.ForeignKey('ngen.Event', on_delete=models.CASCADE, related_name='todos')
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True)
    note = models.TextField(null=True)
    assigned_to = models.ForeignKey('ngen.User', null=True, related_name="assigned_tasks", on_delete=models.PROTECT)

    def save(self, **kwargs):
        if self.completed:
            self.completed_date = timezone.now()
        super().save()

    class Meta:
        db_table = 'todo_task'
        ordering = ["task__playbook"]
        unique_together = ['task', 'event']
