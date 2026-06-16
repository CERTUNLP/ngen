import logging
import os
import shutil

from PIL import Image
from constance import config
from constance.signals import config_updated
from django.conf import settings
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask
from django.core.cache import cache
from rest_framework.authtoken.models import Token

from ngen.models import ArtifactRelation

import json

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_link_contact_by_email(sender, instance=None, created=False, **kwargs):
    from ngen.models.constituency import Contact

    if not created or not config.AUTO_LINK_CONTACT_BY_EMAIL:
        return

    contacts = Contact.objects.filter(
        username=instance.email, type=Contact.TYPE.email
    )
    for contact in contacts:
        contact.users.add(instance)


@receiver(config_updated)
def config_updated_handler(sender, key, old_value, new_value, **kwargs):
    """
    Callback function for Constance config update
    """
    if new_value is not None:
        cache.set(f"constance:{key}", new_value)

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

    elif (
        key in ["EMAIL_HOST", "EMAIL_PORT", "EMAIL_USERNAME", "EMAIL_PASSWORD"]
        and new_value
    ):
        try:
            task = PeriodicTask.objects.filter(name="retrieve_emails").first()
            if task:
                task.enabled = True
                task.save()
        except Exception:
            logger.debug("Could not re-enable retrieve_emails periodic task", exc_info=True)


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


@receiver(post_save, sender="ngen.TaggedObject")
def audit_taggedobject_change(sender, instance=None, created=False, **kwargs):
    from auditlog.models import LogEntry

    parent = instance.content_object
    if parent is None:
        return

    tag_name = instance.tag.name if instance.tag else "unknown"
    changes = {"tags": ["", f"{'added' if created else 'updated'}: {tag_name}"]}
    LogEntry.objects.log_create(
        instance=parent,
        action=LogEntry.Action.UPDATE,
        changes=json.dumps(changes),
    )


@receiver(post_delete, sender="ngen.TaggedObject")
def audit_taggedobject_remove(sender, instance=None, **kwargs):
    from auditlog.models import LogEntry

    parent = instance.content_object
    if parent is None:
        return

    tag_name = instance.tag.name if instance.tag else "unknown"
    changes = {"tags": ["", f"removed: {tag_name}"]}
    LogEntry.objects.log_create(
        instance=parent,
        action=LogEntry.Action.UPDATE,
        changes=json.dumps(changes),
    )


_m2m_field_map = {}

def _get_m2m_field_map():
    if not _m2m_field_map:
        from ngen.models.constituency import Contact, Network
        from ngen.models.taxonomy import Playbook
        _m2m_field_map[Network.contacts.through] = ("contacts", "contact")
        _m2m_field_map[Contact.users.through] = ("users", "user")
        _m2m_field_map[Playbook.taxonomy.through] = ("taxonomy", "taxonomy")
    return _m2m_field_map


@receiver(m2m_changed)
def audit_m2m_changes(sender, instance, action, pk_set, **kwargs):
    if action not in ("post_add", "post_remove", "post_clear"):
        return

    from auditlog.models import LogEntry

    info = _get_m2m_field_map().get(sender)
    if not info:
        return

    field_name, related_model = info
    pks = sorted(pk_set)
    changes = {field_name: ["", f"{action} [{related_model}]: {pks}"]}
    LogEntry.objects.log_create(
        instance=instance,
        action=LogEntry.Action.UPDATE,
        changes=json.dumps(changes),
    )
