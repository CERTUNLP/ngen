import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.db import IntegrityError
from django.db.models import Q
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from ngen.models import User
from ngen.services.login_attempts import LoginAttemptLimiter

logger = logging.getLogger(__name__)


class EmailOrUsernameModelBackend(ModelBackend):
    """
    The plain login accepts the username or the email, and neither of them by
    case: the same account is reachable from the login page, the api, the admin
    and the browsable api, which all go through django's authenticate().
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        user = self.get_user_by_identifier(username)
        # The account is what is counted, not how it was named: otherwise the
        # same account can be tried twice over, once by username and once by
        # email. An identifier that reaches nobody is counted as itself
        limiter = LoginAttemptLimiter(f"user:{user.pk}" if user else username, request)
        if limiter.is_locked():
            logger.warning("Login refused, too many failed attempts")
            return None

        if user is None:
            # Same work as a real login, so that a wrong user and a wrong
            # password do not take a different time to answer
            User().set_password(password)
            limiter.register_failure()
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            limiter.reset()
            return user

        limiter.register_failure()
        return None

    def get_user_by_identifier(self, identifier):
        """
        The user whose username or email is the given one, or nothing if it
        does not single one out
        """
        users = list(
            User.objects.filter(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            )[:3]
        )
        if len(users) == 1:
            return users[0]
        if not users:
            return None

        # Usernames are only unique as written, so an identifier can reach more
        # than one account. The one that owns it as written wins, and anything
        # still ambiguous is refused instead of guessed
        exact = [user for user in users if user.username == identifier]
        if len(exact) == 1:
            return exact[0]
        logger.warning("Login identifier matches %s users, refusing", len(users))
        return None


class NgenOidcBackend(OIDCAuthenticationBackend):
    def get_user_by_email(self, email):
        users = list(User.objects.filter(email__iexact=email)[:2])
        if len(users) == 1:
            return users[0]
        if len(users) > 1:
            # Cannot happen since the email is unique, but guessing which
            # account an identity owns is not something to do by accident
            logger.error("More than one user with the email %s, refusing", email)
        return None

    def create_user(self, claims):
        email_claim = settings.OIDC_EMAIL_CLAIM or "email"
        username_claim = settings.OIDC_USERNAME_CLAIM or "preferred_username"
        first_name_claim = settings.OIDC_FIRST_NAME_CLAIM or "given_name"
        last_name_claim = settings.OIDC_LAST_NAME_CLAIM or "family_name"

        email = claims.get(email_claim, "")
        username = claims.get(username_claim, email)

        if not username:
            username = email.split("@")[0] if "@" in email else email

        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=claims.get(first_name_claim, ""),
            last_name=claims.get(last_name_claim, ""),
        )
        user.set_unusable_password()
        user.save()
        return user

    def filter_users_by_claims(self, claims):
        email_claim = settings.OIDC_EMAIL_CLAIM or "email"
        email = claims.get(email_claim)
        if not email:
            return User.objects.none()
        user = self.get_user_by_email(email)
        if user:
            return [user]
        return User.objects.none()

    def update_user(self, user, claims):
        email_claim = settings.OIDC_EMAIL_CLAIM or "email"
        first_name_claim = settings.OIDC_FIRST_NAME_CLAIM or "given_name"
        last_name_claim = settings.OIDC_LAST_NAME_CLAIM or "family_name"

        email = claims.get(email_claim, "")
        first_name = claims.get(first_name_claim, "")
        last_name = claims.get(last_name_claim, "")

        updated = False
        if email and user.email.lower() != email.lower():
            if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
                logger.warning(
                    "Skipping email update for user %s: %s already taken",
                    user.pk, email,
                )
            else:
                user.email = email
                updated = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True

        if updated:
            try:
                user.save()
            except IntegrityError:
                logger.exception("Failed to update user %s", user.pk)

        return user

    def verify_claims(self, claims):
        email_claim = settings.OIDC_EMAIL_CLAIM or "email"
        email = claims.get(email_claim)
        if not email:
            return False
        email_verified = claims.get("email_verified")
        if email_verified is False:
            return False

        # Check required group membership
        required_group = getattr(settings, "OIDC_REQUIRED_GROUP", "")
        if required_group:
            groups = claims.get("groups", [])
            # Keycloak includes groups as "/group-name" or "group-name"
            normalized_groups = [g.lstrip("/") for g in groups]
            if required_group not in normalized_groups:
                logger.warning(
                    "SSO login denied: user %s not in required group '%s' (groups: %s)",
                    email, required_group, normalized_groups,
                )
                return False

        return True

    def authenticate(self, request, claims=None, id_token=None, access_token=None):
        if not claims:
            return None
        if not self.verify_claims(claims):
            return None

        email_claim = settings.OIDC_EMAIL_CLAIM or "email"
        email = claims.get(email_claim)
        if not email:
            return None

        users = self.filter_users_by_claims(claims)

        if users:
            user = users[0]
            if not user.is_active:
                logger.warning("SSO login attempt for inactive user %s", user.pk)
                return None
            user = self.update_user(user, claims)
        elif settings.OIDC_CREATE_USER:
            user = self.create_user(claims)
        else:
            return None

        return user
