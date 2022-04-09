from datetime import timedelta

from constance import config
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify

from .utils import NgenModel, NgenPriorityMixin


class Feed(NgenModel):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    active = models.IntegerField()
    description = models.CharField(max_length=250, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(Feed, self).save(*args, **kwargs)

    class Meta:
        db_table = 'feed'

    def __str__(self):
        return self.name


class Priority(NgenModel):
    name = models.CharField(max_length=255)
    severity = models.IntegerField(unique=True)

    attend_time = models.DurationField(default=timedelta(minutes=config.PRIORITY_ATTEND_TIME_DEFAULT))
    solve_time = models.DurationField(default=timedelta(minutes=config.PRIORITY_SOLVE_TIME_DEFAULT))

    attend_deadline = models.DurationField(default=timedelta(minutes=config.PRIORITY_ATTEND_DEADLINE_DEFAULT))
    solve_deadline = models.DurationField(default=timedelta(minutes=config.PRIORITY_SOLVE_DEADLINE_DEFAULT))

    @classmethod
    def default_priority(cls):
        return cls.objects.get(name='Medium')

    class Meta:
        db_table = 'priority'
        ordering = ['severity']

    def __str__(self):
        return self.name


class Tlp(NgenModel):
    slug = models.SlugField(max_length=100, unique=True)
    rgb = models.CharField(max_length=45)
    when = models.TextField(max_length=500)
    why = models.TextField(max_length=500, )
    information = models.TextField(max_length=10, )
    description = models.TextField(max_length=150)
    encrypt = models.BooleanField(default=False)
    name = models.CharField(max_length=45)
    code = models.IntegerField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(Tlp, self).save(*args, **kwargs)

    class Meta:
        db_table = 'tlp'

    def __str__(self):
        return self.name


class User(AbstractUser, NgenPriorityMixin):
    api_key = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'user'
