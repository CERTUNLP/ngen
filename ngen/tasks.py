from celery import shared_task
from constance import config
from django.db.models import F, DateTimeField, ExpressionWrapper, DurationField
from django.utils import timezone
from django.utils.translation import gettext_lazy

import ngen.models
from ngen import cortex
from ngen.models.announcement import Communication
from ngen.services.contact_lookup import ContactLookupService


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def attend_cases():
    cases = ngen.models.Case.objects.annotate(
        deadline=ExpressionWrapper(
            F("created") + F("priority__attend_time"), output_field=DateTimeField()
        )
    ).filter(
        attend_date__isnull=True,
        solve_date__isnull=True,
        deadline__lte=timezone.now(),
        lifecycle__in=["auto", "auto_open"],
    )
    cases.update(attend_date=timezone.now())
    for case in cases:
        case.communicate_open()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def solve_cases():
    cases = ngen.models.Case.objects.annotate(
        deadline=ExpressionWrapper(
            F("attend_date") + F("priority__solve_time"), output_field=DateTimeField()
        )
    ).filter(
        attend_date__isnull=False,
        solve_date__isnull=True,
        deadline__lte=timezone.now(),
        lifecycle__in=["auto", "auto_close"],
    )
    cases.update(solve_date=timezone.now())
    for case in cases:
        case.communicate_close()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def case_renotification():
    cases = (
        ngen.models.Case.objects.annotate(
            deadline=ExpressionWrapper(
                F("priority__solve_time")
                * (F("notification_count") / F("priority__notification_amount")),
                output_field=DurationField(),
            )
        )
        .annotate(
            renotification=ExpressionWrapper(
                F("attend_date") + F("deadline"), output_field=DateTimeField()
            )
        )
        .filter(
            attend_date__isnull=False,
            solve_date__isnull=True,
            renotification__lte=timezone.now(),
            notification_count__gte=1,
        )
    )
    cases.update(notification_count=F("notification_count") + 1)
    for case in cases:
        case.communicate(
            gettext_lazy("Renotification: New Case"), "reports/case_report.html"
        )


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def contact_summary(contacts=None, tlp=None):
    """
    Send summary of open cases to all network admins
    """
    if contacts is None:
        contacts = ngen.models.Contact.objects.filter(type="email")

    tlp = tlp.lower() if tlp else config.SUMMARY_TLP.lower()
    tlp_obj = ngen.models.Tlp.objects.get(slug=tlp) if tlp and tlp != "none" else None

    for contact in contacts:
        # Get all open cases for the contact
        open_cases = ngen.models.Case.objects.filter(
            state__attended=True, events__network__contacts=contact
        ).prefetch_related("events")
        list_open_cases = [
            {"case": case, "events": case.events.filter(network__contacts=contact)}
            for case in open_cases
        ]

        # Get all closed cases for the contact of last week
        closed_cases = ngen.models.Case.objects.filter(
            state__solved=True,
            events__network__contacts=contact,
            solve_date__gte=timezone.now()
            - timezone.timedelta(days=config.SUMMARY_DAYS),
        ).prefetch_related("events")
        list_closed_cases = [
            {"case": case, "events": case.events.filter(network__contacts=contact)}
            for case in closed_cases
        ]

        if open_cases or closed_cases:
            Communication.communicate_contact_summary(
                contact,
                list_open_cases,
                list_closed_cases,
                tlp_obj,
            )


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def create_cases_for_matching_events(template_id):
    template = ngen.models.CaseTemplate.objects.get(pk=template_id)
    template.create_cases_for_matching_events()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def enrich_artifact(artifact_id):
    api = cortex.api_user
    if not api:
        return "Cortex down"
    artifact = ngen.models.Artifact.objects.get(pk=artifact_id)
    print("Enrichment for {}".format(artifact))
    if artifact.type in config.ALLOWED_ARTIFACTS_TYPES.split(","):
        jobs = []
        artifact.enrichments.all().delete()
        analyzers = api.analyzers.get_by_type(artifact.type)
        for analyzer in analyzers:
            jobs.append(
                api.analyzers.run_by_id(
                    analyzer.id, {"data": artifact.value, "dataType": artifact.type}
                )
            )

        while jobs:
            for job in jobs:
                report = api.jobs.get_report(job.id)
                save_if_fail = (
                    report.status == "Failure"
                    and config.ARTIFACT_SAVE_ENRICHMENT_FAILURE
                )
                if report.status == "Success" or save_if_fail:
                    ngen.models.ArtifactEnrichment.objects.create(
                        artifact=artifact,
                        name=report.workerName,
                        raw=report.report,
                        success=report.report.get("success"),
                    )
                    if config.ARTIFACT_RECURSIVE_ENRICHMENT:
                        for job_artifact in api.jobs.get_artifacts(job.id):
                            if (
                                job_artifact.dataType
                                in config.ALLOWED_ARTIFACTS_TYPES.split(",")
                            ):
                                new_artifact, created = (
                                    ngen.models.Artifact.objects.get_or_create(
                                        value=job_artifact.data,
                                        defaults={"type": job_artifact.dataType},
                                    )
                                )
                                for relation in artifact.artifact_relation.all():
                                    ngen.models.ArtifactRelation.objects.get_or_create(
                                        artifact=new_artifact,
                                        content_type=relation.content_type,
                                        object_id=relation.object_id,
                                    )
                                if not created:
                                    new_artifact.enrich()
                    jobs.remove(job)


@shared_task(bind=True)
def whois_lookup_task(self, ip_or_domain):
    """
    Tarea de Celery para hacer una búsqueda WHOIS.
    """
    try:
        whois_data = ContactLookupService.get_contact_info(ip_or_domain)
        return whois_data
    except Exception as e:
        return {"error": str(e)}
