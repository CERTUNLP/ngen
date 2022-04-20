from datetime import datetime

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy
from django_bleach.models import BleachField
from model_utils import Choices

from .utils import NgenModel, NgenTreeModel, NgenPriorityMixin


class Taxonomy(NgenModel, NgenTreeModel):
    TYPE = Choices(('vulnerability', gettext_lazy('Vulnerability')), ('incident', gettext_lazy('Incident')))
    type = models.CharField(choices=TYPE, default=TYPE.vulnerability, max_length=20)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True)
    node_order_by = ['id']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(Taxonomy, self).save(*args, **kwargs)

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


class Report(NgenModel):
    LANG = Choices('en', 'es')
    lang = models.CharField(choices=LANG, default=LANG.en, max_length=2)
    taxonomy = models.ForeignKey(Taxonomy, models.CASCADE, related_name='reports')
    problem = BleachField()
    derived_problem = BleachField(null=True)
    verification = BleachField(null=True)
    recommendations = BleachField(null=True)
    more_information = BleachField(null=True)

    class Meta:
        db_table = 'report'
        unique_together = ['lang', 'taxonomy']

    def __str__(self):
        return "%s (%s)" % (self.taxonomy.name, self.lang)


class Playbook(NgenModel):
    name = models.CharField(max_length=60)
    taxonomy = models.ManyToManyField('Taxonomy', related_name='playbooks')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'playbook'
        ordering = ["name"]


class Task(NgenModel, NgenPriorityMixin):
    name = models.CharField(max_length=140)
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'task'
        ordering = ["priority__severity"]


class TodoTask(NgenModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='todos')
    event = models.ForeignKey('ngen.Event', on_delete=models.CASCADE, related_name='todos')
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True)
    note = models.TextField(null=True)
    assigned_to = models.ForeignKey('ngen.User', null=True, related_name="assigned_tasks", on_delete=models.DO_NOTHING)

    def save(self, **kwargs):
        if self.completed:
            self.completed_date = datetime.now()
        super().save()

    class Meta:
        db_table = 'todo_task'
        ordering = ["task__playbook"]
        unique_together = ['task', 'event']
