from auditlog.registry import auditlog
from django.apps import apps

from .administration import *
from .announcement import *
from .artifact import *
from .case import *
from .constituency import *
from .message import *
from .state import *
from .taxonomy import *
from .utils import *

for model in apps.all_models['ngen'].values():
    if issubclass(model, NgenModel):
        auditlog.register(model)

# User creation auth token
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
