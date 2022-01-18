import os
import re

from django.core import mail
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy


class Mailer:

    def send_mail(self, subject, template, from_mail, recipient_list, lang):
        html_content = get_template(template).render({'html': True, 'lang': lang})
        text_content = re.sub(r'\n+', '\n', strip_tags(get_template(template).render({'lang': lang})).replace('  ', ''))
        mail.send_mail(subject, text_content, from_mail, recipient_list, html_message=html_content)

    def case_creation(self, case):
        for contact in case.contacts():
            self.send_mail(gettext_lazy('[%s][TLP:%s][ID:%s]' % ('CERTUNLP', case.tlp, case.id)), 'reports/base.html',
                           os.environ.get(DJANGO_SUPERUSER_EMAIL),
                           contact, 'en')
