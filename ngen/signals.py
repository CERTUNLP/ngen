import os
import shutil
from PIL import Image

from constance import config
import constance
from djangoProject import settings
from constance.signals import config_updated
from django.dispatch import receiver

@receiver(config_updated)
def team_logo_updated(sender, key, old_value, new_value, **kwargs):
    print('modified field', key, old_value, new_value, settings.CONSTANCE_CONFIG['TEAM_LOGO'][0])
    if key == 'TEAM_LOGO' and new_value and new_value != settings.CONSTANCE_CONFIG['TEAM_LOGO'][0]:
        new_file = os.path.join(settings.MEDIA_ROOT, new_value)

        print(new_file)
        if os.path.exists(new_file):
            print('exists')
            if new_file != settings.LOGO_PATH:
                shutil.copy(new_file, settings.LOGO_PATH)
                os.remove(new_file)

            image = Image.open(settings.LOGO_PATH)
            # A max size of 200 x 50
            image.thumbnail((200,50))
            image.save(settings.LOGO_PATH_200_50)

            config.TEAM_LOGO = settings.CONSTANCE_CONFIG['TEAM_LOGO'][0]
