from django.db import models

from .case import NgenModel


class Feed(NgenModel):
    slug = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    active = models.IntegerField()
    description = models.CharField(max_length=250, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'feed'


class Priority(NgenModel):
    name = models.CharField(max_length=255)
    response_time = models.IntegerField()
    solve_time = models.IntegerField()
    code = models.IntegerField()
    unresponse_time = models.IntegerField()
    unsolve_time = models.IntegerField()
    active = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'priority'


class Tlp(NgenModel):
    slug = models.CharField(max_length=45)
    rgb = models.CharField(max_length=45)
    when = models.TextField(max_length=500)
    why = models.TextField(max_length=500, )
    information = models.TextField(max_length=10, )
    description = models.TextField(max_length=150)
    encrypt = models.BooleanField(default=False)
    name = models.CharField(max_length=45)
    code = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'tlp'


class User(NgenModel):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.CharField(max_length=180)
    username = models.CharField(max_length=180)
    password = models.CharField(max_length=255)
    salt = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=100, blank=True, null=True)
    enabled = models.IntegerField()
    username_canonical = models.CharField(unique=True, max_length=180)
    email_canonical = models.CharField(unique=True, max_length=180)
    last_login = models.DateTimeField(blank=True, null=True)
    confirmation_token = models.CharField(unique=True, max_length=180, blank=True, null=True)
    password_requested_at = models.DateTimeField(blank=True, null=True)
    roles = models.TextField()
    created_by = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'user'
