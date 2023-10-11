from datetime import timedelta

from colorfield.fields import ColorField
from constance import config
from django.db import models

from ngen.models.common.mixins import AuditModelMixin
from ngen.utils import slugify_underscore


class Feed(AuditModelMixin):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=250, null=True, blank=True, default='')

    def save(self, *args, **kwargs):
        self.slug = slugify_underscore(self.name)
        super(Feed, self).save(*args, **kwargs)

    class Meta:
        db_table = 'feed'

    def __str__(self):
        return self.name


COLOR_PALETTE = [
    ("#FFFFFF", "white",),
    ("#000000", "black",),
]


class Priority(AuditModelMixin):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    severity = models.IntegerField(unique=True)
    attend_time = models.DurationField(default=timedelta(minutes=config.PRIORITY_ATTEND_TIME_DEFAULT))
    solve_time = models.DurationField(default=timedelta(minutes=config.PRIORITY_SOLVE_TIME_DEFAULT))
    notification_amount = models.PositiveSmallIntegerField(default=3)
    color = ColorField(samples=COLOR_PALETTE)

    def save(self, *args, **kwargs):
        self.slug = slugify_underscore(self.name)
        super(Priority, self).save(*args, **kwargs)

    @classmethod
    def default_priority(cls):
        return cls.objects.get(name=config.PRIORITY_DEFAULT)

    class Meta:
        db_table = 'priority'
        ordering = ['severity']

    def __str__(self):
        return self.name


class Tlp(AuditModelMixin):
    slug = models.SlugField(max_length=100, unique=True)
    color = ColorField(samples=COLOR_PALETTE)
    when = models.TextField(max_length=500)
    why = models.TextField(max_length=500, )
    information = models.TextField(max_length=10, )
    description = models.TextField(max_length=150)
    encrypt = models.BooleanField(default=False)
    name = models.CharField(max_length=45)
    code = models.IntegerField()

    def save(self, *args, **kwargs):
        self.slug = slugify_underscore(self.name)
        super(Tlp, self).save(*args, **kwargs)

    class Meta:
        db_table = 'tlp'

    def __str__(self):
        return self.name
