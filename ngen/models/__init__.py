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
