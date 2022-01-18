import re

from celery import shared_task
from django.core import mail
from django.template.loader import get_template
from django.utils.html import strip_tags


