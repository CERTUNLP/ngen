import re

from constance import config
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy

from ngen.models import Case, Priority


class Communication:
    @staticmethod
    def send_mail(subject, content: dict, from_mail: str, recipient_list: list, bcc_list: list = None,
                  attachments: dict = None, extra_headers: dict = None):
        email = EmailMultiAlternatives(subject, content['text'], from_mail, recipient_list, bcc=bcc_list)
        email.attach_alternative(content['html'], "text/html")
        if extra_headers:
            email.extra_headers.update(extra_headers)
        for name, file in attachments:
            email.attach(name, file)
        email.send()

    @staticmethod
    def render_template(template: str, lang: str = None, extra_params: dict = None) -> dict:
        content = {}
        lang = lang if lang else config.NGEN_LANG
        params = {'lang': lang, 'config': config}
        if extra_params:
            params.update(extra_params)
        content['text'] = re.sub(r'\n+', '\n', strip_tags(get_template(template).render(params)).replace('  ', ''))
        params.update({'html': True})
        content['html'] = get_template(template).render(params)
        return content


class CommunicationCase(Communication):

    @staticmethod
    def bcc_recipient_list(case):
        bcc = []
        priority = Priority.objects.get(name=config.TEAM_EMAIL_PRIORITY)
        if case.assigned and case.assigned.priority.severity >= case.priority.severity:
            bcc.append([case.assigned.email])
        if config.TEAM_EMAIL and priority.severity >= case.priority.severity:
            bcc.append([config.TEAM_EMAIL])
        return bcc

    @staticmethod
    def email_subject(case: 'Case', title: str):
        return '[%s][TLP:%s][ID:%s] %s' % (config.TEAM_NAME, gettext_lazy(case.tlp.name), case.id, title)

    def communicate(self, title: str, template: str, recipient_list: list, case: 'Case', events: list = None):
        return self.send_mail(self.email_subject(case, title),
                              self.render_template(template, extra_params={'case': case, 'events': events}),
                              config.EMAIL_SENDER, recipient_list, self.bcc_recipient_list(case), case.attachments,
                              {'Message-ID': case.report_message_id})

    def communicate_case(self, case, title: str, template: str):
        for contacts, events in case.events_by_contacts().items():
            self.communicate(title, template, [c.username for c in contacts], case,
                             events)

    def case_assign_communication(self, event):
        if event.case.events.count() >= 1:
            self.communicate(gettext_lazy('New event on case'), 'reports/case_assign.html',
                             [c.username for c in event.email_contacts()], event.case, [event])

    def state_change_communication(self, case):
        self.communicate_case(case, gettext_lazy('Case status updated'), 'reports/state_change.html')
