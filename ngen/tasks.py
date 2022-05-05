import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from constance import config
from django.db.models import F, DateTimeField, ExpressionWrapper

import ngen.cortex as cortex
import ngen.models

logger = get_task_logger(__name__)


@shared_task()
def attend_cases():
    return 'Attended cases: %s' % ngen.models.Case.objects.annotate(
        deadline=ExpressionWrapper(F('created') + F('priority__attend_time') + F('priority__attend_deadline'),
                                   output_field=DateTimeField())).filter(attend_date__isnull=True,
                                                                         solve_date__isnull=True,
                                                                         deadline__lte=datetime.datetime.now(),
                                                                         lifecycle__in=['auto', 'auto_open']).update(
        attend_date=datetime.datetime.now())


@shared_task
def solve_cases():
    return 'Solved cases: %s' % ngen.models.Case.objects.annotate(
        deadline=ExpressionWrapper(F('attend_date') + F('priority__solve_time') + F('priority__solve_deadline'),
                                   output_field=DateTimeField())).filter(attend_date__isnull=False,
                                                                         solve_date__isnull=True,
                                                                         deadline__lte=datetime.datetime.now(),
                                                                         lifecycle__in=['auto', 'auto_close']).update(
        solve_date=datetime.datetime.now())


@shared_task()
def enrich_artifact(artifact_id):
    artifact = ngen.models.Artifact.objects.get(pk=artifact_id)
    print("Enrichment for {}".format(artifact))
    if artifact.type in config.ALLOWED_ARTIFACTS_TYPES.split(','):
        jobs = []
        analyzers = cortex.api_user.analyzers.get_by_type(artifact.type)
        for analyzer in analyzers:
            jobs.append(
                cortex.api_user.analyzers.run_by_id(analyzer.id, {'data': artifact.value, 'dataType': artifact.type}))

        while jobs:
            for job in jobs:
                report = cortex.api_user.jobs.get_report(job.id)
                if report.status == 'Success' or (
                        report.status == 'Failure' and config.ARTIFACT_SAVE_ENRICHMENT_FAILURE):
                    ngen.models.ArtifactEnrichment.objects.filter(artifact=artifact, name=report.workerName).delete()
                    ngen.models.ArtifactEnrichment.objects.create(artifact=artifact, name=report.workerName,
                                                                  raw=report.report,
                                                                  success=report.report.get('success'))
                for job_artifact in cortex.api_user.jobs.get_artifacts(job.id):
                    if job_artifact.dataType in config.ALLOWED_ARTIFACTS_TYPES.split(','):
                        new_artifact = ngen.models.Artifact.objects.get_or_create(type=job_artifact.dataType,
                                                                                  value=job_artifact.data)
                        for relation in artifact.artifact_relation.all():
                            ngen.models.ArtifactRelation.objects.get_or_create(artifact=new_artifact[0],
                                                                               content_type=relation.content_type,
                                                                               object_id=relation.object_id)
                jobs.remove(job)
