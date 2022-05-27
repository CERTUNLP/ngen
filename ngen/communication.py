import re

from constance import config
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags


class Communication:
    @staticmethod
    def send_mail(subject, content: dict, recipients: dict[str, list], attachments: list[dict] = None,
                  extra_headers: dict = None):
        email = EmailMultiAlternatives(subject, content['text'], recipients['from'],
                                       recipients['to'], bcc=recipients['bcc'], cc=recipients['cc'])
        email.attach_alternative(content['html'], "text/html")
        email.extra_headers.update(extra_headers)
        for attachment in attachments:
            email.attach(attachment['name'], attachment['file'].read())
        email.send()

    @staticmethod
    def render_template(template: str, extra_params: dict = None, lang: str = None) -> dict:
        content = {}
        lang = lang if lang else config.NGEN_LANG
        params = {'lang': lang, 'config': config}
        if extra_params:
            params.update(extra_params)
        content['text'] = re.sub(r'\n+', '\n', strip_tags(get_template(template).render(params)).replace('  ', ''))
        params.update({'html': True})
        content['html'] = get_template(template).render(params)
        return content

    def communicate(self, title: str, template: str, **kwargs):
        return self.send_mail(self.subject(title), self.render_template(template, extra_params=self.template_params),
                              self.recipients, self.email_attachments, self.email_headers)

    def subject(self, title: str = None) -> str:
        raise NotImplementedError

    @property
    def recipients(self) -> dict[str, list]:
        raise NotImplementedError

    @property
    def template_params(self) -> dict:
        raise NotImplementedError

    @property
    def email_headers(self) -> dict:
        raise NotImplementedError

    @property
    def email_attachments(self) -> list[dict]:
        raise NotImplementedError
