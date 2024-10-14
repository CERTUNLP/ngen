from auditlog.registry import auditlog
from django.apps import apps

from .administration import *  # noqa: F401
from .announcement import *  # noqa: F401
from .artifact import *  # noqa: F401
from .auth import *  # noqa: F401
from .case import *  # noqa: F401
from .common import *  # noqa: F401
from .common.mixins import *  # noqa: F401
from .communication_channel import *  # noqa: F401
from .constituency import *  # noqa: F401
from .email_message import *  # noqa: F401
from .message import *  # noqa: F401
from .state import *  # noqa: F401
from .taxonomy import *  # noqa: F401
from .common.permission import *  # noqa: F401

for model in apps.all_models["ngen"].values():
    if issubclass(model, AuditModelMixin):
        auditlog.register(model)
