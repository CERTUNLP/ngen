from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from ngen.models.common.mixins import (
    AuditModelMixin,
    PriorityModelMixin,
    ValidationModelMixin,
)


class User(AbstractUser, PriorityModelMixin, AuditModelMixin, ValidationModelMixin):
    # The email identifies the user: it is what the login accepts besides the
    # username and what links an account to its identity on the sso provider
    email = models.EmailField(_("email address"), unique=True)
    api_key = models.CharField(max_length=255, blank=True, null=True, default=None)

    class Meta:
        db_table = "user"

    def clean(self):
        super().clean()
        # Stored in a single shape, so that looking it up is an equality and
        # two users cannot differ only in the case of their email
        self.email = (self.email or "").lower()

    @property
    def is_network_admin(self):
        return self.contacts.exists()
