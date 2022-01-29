import re

from constance import config
from django.core import mail
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy

from ngen.models import Priority


def send_mail(subject, template, from_mail, recipient_list, lang, case):
    html_content = get_template(template).render({'html': True, 'lang': lang, 'case': case, 'config': config})
    text_content = re.sub(r'\n+', '\n',
                          strip_tags(
                              get_template(template).render({'lang': lang, 'case': case, 'config': config})).replace(
                              '  ', ''))
    mail.send_mail(subject, text_content, from_mail, recipient_list, html_message=html_content)


def email_subject(case):
    return '[%s][TLP:%s][ID:%s] %s' % (config.TEAM_NAME, gettext_lazy(case.tlp.name), case.id, gettext_lazy('New case'))


def case_creation(case):
    send_mail(email_subject(case), 'reports/newsletter.html', config.EMAIL_SENDER,
              [c.username for c in case.email_contacts()],
              config.NGEN_LANG, case)

    if case.assigned and case.assigned.priority.code >= case.priority.code:
        send_mail(email_subject(case), 'reports/newsletter.html', config.EMAIL_SENDER, [case.assigned.email],
                  config.NGEN_LANG, case)

    if config.TEAM_EMAIL and Priority.objects.get(name=config.TEAM_EMAIL_PRIORITY).code >= case.priority.code:
        send_mail(email_subject(case), 'reports/newsletter.html', config.EMAIL_SENDER, [config.TEAM_EMAIL],
                  config.NGEN_LANG, case)
