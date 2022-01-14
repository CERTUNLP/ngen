import re

from celery import shared_task
from django.core import mail
from django.template.loader import get_template
from django.utils.html import strip_tags


@shared_task
def add(x, y):
    mail.send_mail('subject',
                   re.sub(r'\n+', '\n', strip_tags(get_template('reports/base.html').render()).replace('  ', '')),
                   'dude@aol.com', ['mr@lebowski.com'],
                   html_message=get_template('reports/base.html').render({'html': True}))
