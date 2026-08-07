import hashlib
import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class LoginAttemptLimiter:
    """
    Counts the failed logins of an account from an address and refuses to keep
    trying once there have been too many, which is what makes guessing a
    password cost something.

    It lives in the authentication backend rather than in a view, so that every
    way in is counted the same: the api, the django admin and the browsable api
    all end up calling authenticate().

    The count is kept per account **and** address so that an attacker cannot
    lock an account out of its own owner by failing on purpose.
    """

    prefix = "login_failures"

    def __init__(self, identifier, request=None):
        self.identifier = (identifier or "").strip().lower()
        self.ip = self.client_ip(request)

    @classmethod
    def client_ip(cls, request):
        if request is None:
            return ""
        if settings.LOGIN_TRUST_FORWARDED_FOR:
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
            if forwarded:
                return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    @property
    def key(self):
        # Hashed because the identifier is an email or a username and the cache
        # is shared with the rest of the deployment
        seed = f"{self.identifier}|{self.ip}".encode()
        return f"{self.prefix}_{hashlib.sha256(seed).hexdigest()}"

    @property
    def max_attempts(self):
        return settings.LOGIN_MAX_ATTEMPTS

    def is_locked(self):
        if self.max_attempts <= 0:
            return False
        return cache.get(self.key, 0) >= self.max_attempts

    def register_failure(self):
        """
        Count a failure, keeping the window running from the first one so that
        the block cannot be pushed away by failing slowly
        """
        failures = cache.get(self.key, 0) + 1
        if failures == 1:
            cache.set(self.key, failures, timeout=settings.LOGIN_ATTEMPTS_TIMEOUT)
        else:
            try:
                cache.incr(self.key)
            except ValueError:
                # The window expired between reading and counting
                cache.set(self.key, failures, timeout=settings.LOGIN_ATTEMPTS_TIMEOUT)

        if failures == self.max_attempts:
            logger.warning(
                "Login blocked for %s attempts from %s", failures, self.ip or "unknown"
            )
        return failures

    def reset(self):
        cache.delete(self.key)
