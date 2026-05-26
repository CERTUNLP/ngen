import logging

from constance import config
from django.db import IntegrityError
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from ngen.models import User

logger = logging.getLogger(__name__)


class NgenOidcBackend(OIDCAuthenticationBackend):
    def get_user_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def create_user(self, claims):
        email_claim = config.OIDC_EMAIL_CLAIM or "email"
        username_claim = config.OIDC_USERNAME_CLAIM or "preferred_username"
        first_name_claim = config.OIDC_FIRST_NAME_CLAIM or "given_name"
        last_name_claim = config.OIDC_LAST_NAME_CLAIM or "family_name"

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
        email_claim = config.OIDC_EMAIL_CLAIM or "email"
        email = claims.get(email_claim)
        if not email:
            return User.objects.none()
        user = self.get_user_by_email(email)
        if user:
            return [user]
        return User.objects.none()

    def update_user(self, user, claims):
        email_claim = config.OIDC_EMAIL_CLAIM or "email"
        first_name_claim = config.OIDC_FIRST_NAME_CLAIM or "given_name"
        last_name_claim = config.OIDC_LAST_NAME_CLAIM or "family_name"

        email = claims.get(email_claim, "")
        first_name = claims.get(first_name_claim, "")
        last_name = claims.get(last_name_claim, "")

        updated = False
        if email and user.email != email:
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
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
        email_claim = config.OIDC_EMAIL_CLAIM or "email"
        email = claims.get(email_claim)
        if not email:
            return False
        email_verified = claims.get("email_verified")
        if email_verified is False:
            return False

        # Check required group membership
        required_group = getattr(config, "OIDC_REQUIRED_GROUP", "")
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

        email_claim = config.OIDC_EMAIL_CLAIM or "email"
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
        elif config.OIDC_CREATE_USER:
            user = self.create_user(claims)
        else:
            return None

        return user
