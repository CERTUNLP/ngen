import os
from PIL import Image
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from constance.signals import config_updated

from djangoProject.settings import MEDIA_ROOT
from ngen.models import ArtifactRelation


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


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(config_updated)
def team_logo_updated(sender, key, old_value, new_value, **kwargs):
    if key == "TEAM_LOGO" and new_value:
        old_path = os.path.join(f"{MEDIA_ROOT}", f"{old_value}")
        old_path2 = os.path.join(f"{MEDIA_ROOT}", f"200_50_{old_value}")
        new_path = os.path.join(f"{MEDIA_ROOT}", f"{new_value}")
        new_path2 = os.path.join(f"{MEDIA_ROOT}", f"200_50_{new_value}")

        if os.path.exists(old_path):
            os.remove(old_path)

        if os.path.exists(old_path2):
            os.remove(old_path2)

        image = Image.open(new_path)
        image.resize((200, 50)).save(new_path2)
