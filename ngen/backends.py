from django.db import IntegrityError
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from ngen.models import User
import logging

logger = logging.getLogger(__name__)


class NgenOidcBackend(OIDCAuthenticationBackend):
    def get_user_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def create_user(self, claims):
        email = claims.get("email", "")
        username = claims.get("preferred_username", email)

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
            first_name=claims.get("given_name", ""),
            last_name=claims.get("family_name", ""),
        )
        user.set_unusable_password()
        user.save()
        return user

    def filter_users_by_claims(self, claims):
        email = claims.get("email")
        if not email:
            return User.objects.none()
        user = self.get_user_by_email(email)
        if user:
            return [user]
        return User.objects.none()

    def update_user(self, user, claims):
        email = claims.get("email", "")
        first_name = claims.get("given_name", "")
        last_name = claims.get("family_name", "")

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
        return "email" in claims

    def authenticate(self, request, claims=None, id_token=None, access_token=None):
        from constance import config

        if not claims or not self.verify_claims(claims):
            return None

        email = claims.get("email")
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
