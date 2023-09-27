import os
import shutil
from PIL import Image
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from constance.signals import config_updated
from constance import config

from djangoProject.settings import MEDIA_ROOT
from ngen.models import ArtifactRelation


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(config_updated)
def team_logo_updated(sender, key, old_value, new_value, **kwargs):
    if key == 'TEAM_LOGO' and new_value and new_value != settings.CONSTANCE_CONFIG['TEAM_LOGO'][0]:
        new_file = os.path.join(settings.MEDIA_ROOT, new_value)

        if os.path.exists(new_file):
            if new_file != settings.LOGO_PATH:
                shutil.copy(new_file, settings.LOGO_PATH)
                os.remove(new_file)

            image = Image.open(settings.LOGO_PATH)
            # A max size of 200 x 50
            image.thumbnail((200,50))
            image.save(settings.LOGO_PATH_200_50)

            config.TEAM_LOGO = settings.CONSTANCE_CONFIG['TEAM_LOGO'][0]


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
