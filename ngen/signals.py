import os
import shutil

from PIL import Image
from constance import config
from constance.signals import config_updated
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from ngen.models import ArtifactRelation
from ngen.models.email_message import EmailMessage
from ngen.tasks import async_send_email


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(config_updated)
def team_logo_updated(sender, key, old_value, new_value, **kwargs):
    if (
        key == "TEAM_LOGO"
        and new_value
        and new_value != settings.CONSTANCE_CONFIG["TEAM_LOGO"][0]
    ):
        new_file = os.path.join(settings.MEDIA_ROOT, new_value)

        if os.path.exists(new_file):
            if new_file != settings.LOGO_PATH:
                shutil.copy(new_file, settings.LOGO_PATH)
                os.remove(new_file)

            image = Image.open(settings.LOGO_PATH)
            image.thumbnail(settings.LOGO_WIDE_SIZE)
            image.save(settings.LOGO_WIDE_PATH)

            config.TEAM_LOGO = settings.CONSTANCE_CONFIG["TEAM_LOGO"][0]


@receiver(post_delete, sender=ArtifactRelation)
def artifactrelation_delete_callback(sender, **kwargs):
    obj = kwargs["instance"]
    count = (
        ArtifactRelation.objects.filter(artifact=obj.artifact)
        .exclude(pk=obj.pk)
        .count()
    )
    if count == 0:
        obj.artifact.delete()


@receiver(post_save, sender=EmailMessage)
def send_email_after_create(instance=None, created=False, **_kwargs):
    """
    Send email asynchronously after creating an EmailMessage instance.
    """
    if created:
        async_send_email.delay(instance.id)
