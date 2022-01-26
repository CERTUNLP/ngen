import re

from constance import config
from django.core import mail
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy


def send_mail(subject, template, from_mail, recipient_list, lang):
    html_content = get_template(template).render({'html': True, 'lang': lang})
    text_content = re.sub(r'\n+', '\n', strip_tags(get_template(template).render({'lang': lang})).replace('  ', ''))
    mail.send_mail(subject, text_content, from_mail, recipient_list, html_message=html_content)


def case_creation(case):
    for contact in case.email_contacts():
        send_mail('[%s][TLP:%s][ID:%s]' % (config.TEAM_NAME, gettext_lazy(case.tlp), case.id), 'reports/base.html',
                  config.EMAIL_SENDER,
                  [c.username for c in contact], config.NGEN_LANG)

    if case.assigned:
        send_mail('[%s][TLP:%s][ID:%s]' % (config.TEAM_NAME, gettext_lazy(case.tlp), case.id), 'reports/base.html',
                  config.EMAIL_SENDER,
                  [case.assigned.email], config.NGEN_LANG)
