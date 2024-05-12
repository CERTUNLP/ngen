from auditlog.registry import auditlog
from django.apps import apps

from .administration import *
from .announcement import *
from .artifact import *
from .auth import *
from .case import *
from .common.mixins import AuditModelMixin, CanalizableMixin
from .constituency import *
from .message import *
from .state import *
from .taxonomy import *
from .common import *
from .communication_channel import *
from .email_message import *

for model in apps.all_models['ngen'].values():
    if issubclass(model, AuditModelMixin):
        auditlog.register(model)
