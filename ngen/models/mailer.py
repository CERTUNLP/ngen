import re

from constance import config
from django.core import mail
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy

from ngen.models import Priority


def send_mail(subject, template, from_mail, recipient_list, lang, case, extra_params=None):
    params = {'lang': lang, 'case': case, 'config': config}
    if extra_params:
        params.update(extra_params)
    text_content = re.sub(r'\n+', '\n', strip_tags(get_template(template).render(params)).replace('  ', ''))
    params.update({'html': True})
    html_content = get_template(template).render(params)
    mail.send_mail(subject, text_content, from_mail, recipient_list, html_message=html_content)


def email_subject(case, subject):
    return '[%s][TLP:%s][ID:%s] %s' % (config.TEAM_NAME, gettext_lazy(case.tlp.name), case.id, subject)


def communicate(case, template, subject, params: dict = None):
    if case.email_contacts():
        send_mail(email_subject(case, subject), template, config.EMAIL_SENDER,
                  [c.username for c in case.email_contacts()],
                  config.NGEN_LANG, case, params)

    if case.assigned and case.assigned.priority.code >= case.priority.code:
        send_mail(email_subject(case, subject), template, config.EMAIL_SENDER, [case.assigned.email],
                  config.NGEN_LANG, case, params)

    if config.TEAM_EMAIL and Priority.objects.get(name=config.TEAM_EMAIL_PRIORITY).code >= case.priority.code:
        send_mail(email_subject(case, subject), template, config.EMAIL_SENDER, [config.TEAM_EMAIL],
                  config.NGEN_LANG, case, params)


def case_creation(case):
    communicate(case, 'reports/newsletter.html', gettext_lazy('New Case'))


def case_state_change(case):
    communicate(case, 'reports/state_change.html', gettext_lazy('Case status updated'))


def event_case_assign(event):
    communicate(event.case, 'reports/case_assign.html', gettext_lazy('New event on case'), {'event': event})
