import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import F, DateTimeField, ExpressionWrapper

from ngen.models import Case

logger = get_task_logger(__name__)


@shared_task()
def attend_cases():
    return 'Attended cases: %s' % Case.objects.annotate(
        deadline=ExpressionWrapper(F('created') + F('priority__attend_time') + F('priority__attend_deadline'),
                                   output_field=DateTimeField())).filter(attend_date__isnull=True,
                                                                         solve_date__isnull=True,
                                                                         deadline__lte=datetime.datetime.now(),
                                                                         lifecycle__in=['auto', 'auto_open']).update(
        attend_date=datetime.datetime.now())


@shared_task
def solve_cases():
    return 'Solved cases: %s' % Case.objects.annotate(
        deadline=ExpressionWrapper(F('attend_date') + F('priority__solve_time') + F('priority__solve_deadline'),
                                   output_field=DateTimeField())).filter(attend_date__isnull=False,
                                                                         solve_date__isnull=True,
                                                                         deadline__lte=datetime.datetime.now(),
                                                                         lifecycle__in=['auto', 'auto_close']).update(
        solve_date=datetime.datetime.now())
