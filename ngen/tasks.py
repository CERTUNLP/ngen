# pylint: disable=broad-exception-caught

import logging
from os import path
from celery import shared_task
from django_celery_beat.models import PeriodicTask
from django.db.models import F, DateTimeField, ExpressionWrapper, DurationField
from django.conf import settings
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

logger = logging.getLogger(__name__)


class TaskFailure(Exception):
    pass


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
def contact_summary(
    contact_ids=[], contact_usernames=[], tlp=None, days=None, contact_type="email"
):
    """
    Send summary of open cases to all network admins or specific contacts.

    :param list contact_ids: List of contact IDs to send the summary to. If empty, send to all contacts.
    :param list contact_usernames: List of contact usernames to send the summary to. If empty, send to all contacts.
    :param str tlp: TLP (Traffic Light Protocol) level for the summary, defaults to config.SUMMARY_TLP.
    :param int days: Number of days to look back for closed cases, default is the period of the periodic task if exists or 14 days if not exists.
    :param str contact_type: Type of contact to filter by, defaults to "email".
    """
    if contact_ids or contact_usernames:
        contacts = ngen.models.Contact.objects.filter(
            id__in=contact_ids, type=contact_type
        ) | ngen.models.Contact.objects.filter(
            username__in=contact_usernames, type=contact_type
        )
    else:
        contacts = ngen.models.Contact.objects.filter(type=contact_type)

    tlp = tlp.lower() if tlp else config.SUMMARY_TLP.lower()
    tlp_obj = ngen.models.Tlp.objects.get(slug=tlp) if tlp and tlp != "none" else None

    # Get the interval for the periodic task
    if days is not None:
        timedeltavalue = timezone.timedelta(days=days)
    else:
        task = PeriodicTask.objects.filter(task="ngen.tasks.contact_summary").first()
        if task and task.interval:
            interval = task.interval
            period = interval.period  # 'seconds', 'minutes', 'hours', 'days', 'weeks'
            every = interval.every

            # Create a timedelta object based on the interval
            timedelta_kwargs = {period: every}
            timedeltavalue = timezone.timedelta(**timedelta_kwargs)
        else:
            default_value = 14
            timedeltavalue = timezone.timedelta(days=default_value)
            logger.warning(
                f"No interval found for the periodic task 'ngen.tasks.contact_summary'. Using default value: {default_value} days."
            )

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
            solve_date__gte=timezone.now() - timedeltavalue,
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
                days=int(timedeltavalue.total_seconds() / 86400),
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
    logger.warning("Enrichment for {}".format(artifact))
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
                        allowed_types = config.ALLOWED_ARTIFACTS_TYPES or ""
                        for job_artifact in api.jobs.get_artifacts(job.id):
                            if job_artifact.dataType in allowed_types.split(","):
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


@shared_task(store_errors_even_if_ignored=True)
def export_events_for_email_task(email, days=14):
    """
    Tarea de Celery para exportar eventos en un zip y enviarlos a correo electrónico.
    """
    try:
        contact = ngen.models.Contact.objects.filter(username=email).first()
        if not contact:
            raise ValueError(f"Contact with email {email} not found")

        cases = ngen.models.Case.objects.filter(
            events__network__contacts=contact, state__solved=False
        ).distinct()

        timedeltavalue = timezone.timedelta(days=days)

        # Open cases
        open_cases = ngen.models.Case.objects.filter(
            state__attended=True, events__network__contacts=contact
        ).prefetch_related("events")

        list_open_cases = [
            {"case": case, "events": case.events.filter(network__contacts=contact)}
            for case in open_cases
        ]

        # Events export
        events_to_export = ngen.models.Event.objects.filter(
            network__contacts=contact, case__in=cases
        ).distinct()
        exported_data = ngen.models.Event.export_events_to_zip(events_to_export)

        # Closed cases
        closed_cases = ngen.models.Case.objects.filter(
            state__solved=True,
            events__network__contacts=contact,
            solve_date__gte=timezone.now() - timedeltavalue,
        ).prefetch_related("events")

        list_closed_cases = [
            {"case": case, "events": case.events.filter(network__contacts=contact)}
            for case in closed_cases
        ]

        # TLP
        tlp = config.SUMMARY_TLP.lower()
        tlp_obj = (
            ngen.models.Tlp.objects.get(slug=tlp) if tlp and tlp != "none" else None
        )

        logger.info(f"Task - Sending email to {email}, file: {exported_data}")
        with open(exported_data, "rb") as f:
            Communication.communicate_contact_summary_export(
                contact,
                list_open_cases,
                list_closed_cases,
                tlp_obj,
                days=int(timedeltavalue.total_seconds() / 86400),
                attachments=[{"name": exported_data.name, "file": f}],
            )

        return {"status": "success", "message": f"Cases exported and sent to {email}"}

    except Exception:
        logger.exception(f"Task failed for {email}")
        # raise to let celery handle retries if configured
        raise


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def retest_event_kintun(event_id):
    """
    Tarea de Celery para retestear un evento utilizando Kintun.
    """
    try:
        event = ngen.models.Event.objects.get(pk=event_id)
        analyzer_mapping = ngen.models.AnalyzerMapping.objects.get(
            mapping_from=event.taxonomy
        )
        mapping_to = analyzer_mapping.mapping_to
        analyzer_type = analyzer_mapping.analyzer_type
        analysis_data = {
            "date": timezone.now(),
            "analyzer_type": analyzer_type,
            "vulnerable": False,
            "result": "in_progress",
            "target": event.address_value,
            "scan_type": "in_progress",
            "analyzer_url": "in_progress",
            "event": event,
        }
        event_analysis = ngen.models.EventAnalysis.objects.create(**analysis_data)

        kintun_data = kintun.retest_event_kintun(event, mapping_to)

        event_analysis.vulnerable = kintun_data.get("vulnerable", False)
        event_analysis.result = kintun_data.get("evidence", "")
        event_analysis.scan_type = kintun_data.get("vuln_type", "")
        event_analysis.analyzer_url = kintun_data.get("_id", "")

        event_analysis.save()

        return kintun_data
    except Exception as e:
        try:
            event_analysis.delete()
        except Exception as delete_error:
            return {
                "error": f"Original error: {str(e)}, Deletion error: {str(delete_error)}"
            }
        return {"error": str(e)}


@shared_task(bind=True, max_retries=5)
def async_send_email(self, email_message_id: int):
    """
    Task to send an email asynchronously.

    :param int email_message_id: Email message id to send
    """
    if not email_message_id:
        return {"status": "error", "message": "Email message id not provided"}

    try:
        email_message = ngen.models.EmailMessage.objects.get(id=email_message_id)
    except ngen.models.EmailMessage.DoesNotExist as e:
        if self.request.retries == self.max_retries:
            return {"status": "error", "message": f"Email {email_message_id} not found"}

        exponential_backoff = (self.request.retries + 1) ** 2
        self.retry(exc=e, countdown=exponential_backoff)

    mail_conf = {
        "host": config.EMAIL_HOST,
        "port": config.EMAIL_PORT or 587,
        "use_tls": config.EMAIL_USE_TLS,
        "fail_silently": False,
    }

    if config.EMAIL_USERNAME and config.EMAIL_PASSWORD:
        mail_conf["username"] = config.EMAIL_USERNAME
        mail_conf["password"] = config.EMAIL_PASSWORD

    try:
        email_connection = EmailBackend(**mail_conf)

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
            with open(path.join(settings.MEDIA_ROOT, attachment["file"]), "rb") as file:
                email.attach(attachment["name"], file.read())

        email.send(fail_silently=False)

        email_message.sent = True
        email_message.date = timezone.now()
        return {"status": "success", "message": f"Email {email_message_id} sent"}
    except Exception as e:
        email_message.send_attempt_failed = True
        raise e
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

    if not host or not username or not password:
        deactivated = ""
        task = PeriodicTask.objects.filter(name="retrieve_emails").first()
        if task:
            task.enabled = False
            task.save()
            deactivated = "Task deactivated. "
        raise TaskFailure(
            f"{deactivated}Email configuration not set. EMAIL_HOST: '{host}', EMAIL_USERNAME: '{username}', EMAIL_PASSWORD: ????"
        )

    email_client = None
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

        return {
            "status": "success",
            "message": f"{len(unread_emails)} new email/s stored",
        }

    except ConnectionRefusedError:
        raise TaskFailure(
            f"Connection refused: Server '{host}' with username '{username}' and password *****"
        )

    finally:
        if email_client:
            email_client.logout()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def send_contact_checks(contact_ids=None):
    """
    Sends contact checks to all contacts or a specific list of contact IDs.
    """

    if not config.FRONTEND_PUBLIC_URL:
        raise TaskFailure(
            "Frontend public URL must be configured to send contact checks."
        )

    # Obtener contactos
    contacts = (
        ngen.models.Contact.objects.filter(type="email", id__in=contact_ids)
        if contact_ids
        else ngen.models.Contact.objects.filter(type="email")
    )

    for contact in contacts:
        # Crear el check
        ngen.models.ContactCheck.objects.create(contact=contact)


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def send_contact_check_reminder(check_id):
    """
    Sends a reminder email to the contact to complete the verification form.
    """
    check = ngen.models.ContactCheck.objects.get(pk=check_id)
    Communication.send_contact_check_email(
        contact=check.contact,
        networks=check.contact.networks.all(),
        check=check,
    )


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def send_contact_check_submitted(check_id):
    """
    Sends an email to the team when a contact completes the verification form.
    """
    check = ngen.models.ContactCheck.objects.get(pk=check_id)
    Communication.send_contact_check_submitted(
        contact=check.contact,
        networks=check.contact.networks.all(),
        check=check,
    )
