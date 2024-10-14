import magic
from constance import settings, config
from django.utils.text import slugify

from project import settings as project_settings


def get_settings():
    setting_list = []
    for key, options in settings.CONFIG.items():
        default, help_text = options[0], options[1]
        data = {
            "key": key,
            "default": (
                "******"
                if key in project_settings.CONSTANCE_CONFIG_PASSWORDS
                else default
            ),
            "help_text": help_text,
            "value": (
                "******"
                if key in project_settings.CONSTANCE_CONFIG_PASSWORDS
                else getattr(config, key)
            ),
            "value_type": type(default).__name__,
        }
        setting_list.append(data)

    setting_list = sorted(setting_list, key=lambda x: x["key"])
    return setting_list


def slugify_underscore(text):
    return slugify(text.strip()).replace("-", "_")


def get_mime_type(file):
    """
    Get MIME by reading the header of the file already opened.
    """
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(initial_pos)
    return mime_type
