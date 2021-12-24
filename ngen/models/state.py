from django.db import models
from django.utils.text import slugify

from ngen.models import NgenModel


class IncidentState(NgenModel):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    active = models.IntegerField()
    behavior = models.ForeignKey('StateBehavior', models.DO_NOTHING)
    description = models.CharField(max_length=250, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(IncidentState, self).save(*args, **kwargs)

    class Meta:
        db_table = 'incident_state'


class IncidentStateChange(NgenModel):
    incident_id = models.IntegerField(null=True)
    responsible = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='+')
    date = models.DateTimeField(null=True)
    method = models.CharField(max_length=25)
    state_edge = models.ForeignKey('StateEdge', models.DO_NOTHING, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True, related_name='+')

    class Meta:
        db_table = 'incident_state_change'


class StateBehavior(NgenModel):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=45, null=True)
    description = models.CharField(max_length=250, null=True)
    can_edit_fundamentals = models.IntegerField()
    can_edit = models.IntegerField()
    can_enrich = models.IntegerField()
    can_add_history = models.IntegerField()
    can_communicate = models.IntegerField()
    discr = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(StateBehavior, self).save(*args, **kwargs)

    class Meta:
        db_table = 'state_behavior'


class StateEdge(NgenModel):
    parent = models.ForeignKey(IncidentState, models.DO_NOTHING, related_name='parents')
    child = models.ForeignKey(IncidentState, models.DO_NOTHING, related_name='children')
    discr = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'state_edge'
