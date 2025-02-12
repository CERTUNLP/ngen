# pylint: disable=broad-exception-caught

from celery import shared_task
from django.db.models import F, DateTimeField, ExpressionWrapper, DurationField
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from constance import config

from ngen.mailer.email_client import EmailClient
import ngen.models
from ngen import cortex
from ngen import kintun
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


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def retest_event_kintun(event):
    """
    Tarea de Celery para retestear un evento utilizando Kintun.
    """
    try:
        mapping_to = ngen.models.AnalyzerMapping.objects.get(
            mapping_from=event.taxonomy, analyzer_type="kintun"
        ).mapping_to
        kintun_data = kintun.retest_event_kintun(event, mapping_to)
        analysis_data = {
            "date": timezone.now(),
            "analyzer_type": "kintun",
            "vulnerable": kintun_data.get("vulnerable", False),
            "result": kintun_data.get("evidence", ""),
            "target": event.address_value,
            "scan_type": kintun_data.get("vuln_type", ""),
            "analyzer_url": kintun_data.get("_id", ""),
            "event": event,
        }
        ngen.models.EventAnalysis.objects.create(**analysis_data)
        return kintun_data
    except Exception as e:
        return {"error": str(e)}


@shared_task(bind=True, max_retries=5)
def async_send_email(self, email_message_id: int):
    """
    Task to send an email asynchronously.

    :param int email_message_id: Email message id to send
    """
    if not email_message_id:
        return False

    try:
        email_message = ngen.models.EmailMessage.objects.get(id=email_message_id)
    except ngen.models.EmailMessage.DoesNotExist as e:
        if self.request.retries == self.max_retries:
            return False

        exponential_backoff = (self.request.retries + 1) ** 2
        self.retry(exc=e, countdown=exponential_backoff)

    try:
        host = config.EMAIL_HOST
        username = config.EMAIL_USERNAME
        password = config.EMAIL_PASSWORD
        port = config.EMAIL_PORT
        use_tls = config.EMAIL_USE_TLS

        email_connection = EmailBackend(
            host=host,
            username=username,
            password=password,
            use_tls=use_tls,
            port=port or 587,
            fail_silently=False,
        )

        headers = {
            "Message-ID": email_message.message_id,
        }

        if email_message.parent_message_id:
            headers["References"] = " ".join(email_message.references)
            headers["In-Reply-To"] = email_message.parent_message_id

        email = EmailMultiAlternatives(
            subject=email_message.subject,
            body=email_message.body,
            from_email=email_message.senders[0]["email"],
            to=[recipient["email"] for recipient in email_message.recipients],
            bcc=[recipient["email"] for recipient in email_message.bcc_recipients],
            connection=email_connection,
        )

        if email_message.body_html:
            email.attach_alternative(email_message.body_html, "text/html")

        email.extra_headers = headers

        for attachment in email_message.attachments:
            with attachment["file"] as file:
                email.attach(attachment["name"], attachment["file"].read())

        email.send(fail_silently=False)

        email_message.sent = True
        email_message.date = timezone.now()
        return True
    except Exception:
        email_message.send_attempt_failed = True
        return False
    finally:
        email_message.save()


@shared_task
def retrieve_emails():
    """
    Task to retrieve unread imbox emails.
    Unread emails are stored and marked as read.
    """
    host = config.EMAIL_HOST
    username = config.EMAIL_USERNAME
    password = config.EMAIL_PASSWORD

    try:
        email_client = EmailClient(host=host, username=username, password=password)
        unread_emails = email_client.fetch_unread_emails()
        if unread_emails:
            email_messages = email_client.map_emails(unread_emails)
            created_messages = ngen.models.EmailMessage.objects.bulk_create(
                email_messages
            )
            if len(created_messages) == len(unread_emails):
                email_client.mark_emails_as_read(unread_emails)
        return True
    except Exception:
        return False
