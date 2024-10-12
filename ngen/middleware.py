from auditlog.context import set_actor
from auditlog.middleware import AuditlogMiddleware as _AuditlogMiddleware
from django.utils.functional import SimpleLazyObject

from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from constance import config


# https://github.com/jazzband/django-auditlog/issues/115
class AuditlogMiddleware(_AuditlogMiddleware):
    def __call__(self, request):
        remote_addr = self._get_remote_addr(request)

        user = SimpleLazyObject(lambda: getattr(request, "user", None))

        context = set_actor(actor=user, remote_addr=remote_addr)

        with context:
            return self.get_response(request)


class LanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Obtén el idioma de CONSTANCE_CONFIG
        lang_code = config.NGEN_LANG or settings.LANGUAGE_CODE
        translation.activate(lang_code)
        request.LANGUAGE_CODE = lang_code
