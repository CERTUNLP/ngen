from constance import settings, config
from djangoProject import settings as project_settings

def get_settings():
    setting_list = []
    for key, options in settings.CONFIG.items():
        default, help_text = options[0], options[1]
        data = {'key': key,
                'default': '******' if key in project_settings.CONSTANCE_CONFIG_PASSWORDS else default,
                'help_text': help_text,
                'value': '******' if key in project_settings.CONSTANCE_CONFIG_PASSWORDS else getattr(config, key),
                'value_type': type(default).__name__}
        setting_list.append(data)
    return setting_list
