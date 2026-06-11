import django_filters
import logging
from rest_framework import permissions, filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from constance import config
from ngen import models, serializers
from ngen.mailer.email_handler import EmailHandler
from ngen.tasks import async_send_email

logger = logging.getLogger(__name__)


class EmailMessageFilter(django_filters.FilterSet):
    sent = django_filters.BooleanFilter()
    send_attempt_failed = django_filters.BooleanFilter()
    dispatched = django_filters.BooleanFilter()

    class Meta:
        model = models.EmailMessage
        fields = ["sent", "send_attempt_failed", "dispatched"]


class EmailMessageViewSet(viewsets.ModelViewSet):
    queryset = models.EmailMessage.objects.all().order_by("-created")
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_class = EmailMessageFilter
    search_fields = ["subject"]
    ordering_fields = ["id", "created", "modified", "date", "subject"]
    serializer_class = serializers.EmailMessageListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.EmailMessageListSerializer
        return serializers.EmailMessageSerializer

    @action(detail=True, methods=["post"], url_path="send")
    def send_queued(self, request, pk=None):
        """
        Dispatch a stored email to Celery for sending.
        Only pending emails (not sent, not dispatched, not failed).
        """
        email_message = self.get_object()
        if email_message.sent:
            logger.warning("EmailQueue.send: id=%s already sent, skipping", email_message.id)
            return Response(
                {"error": "Email already sent"}, status=status.HTTP_400_BAD_REQUEST
            )
        if email_message.dispatched and not email_message.send_attempt_failed:
            logger.warning(
                "EmailQueue.send: id=%s stuck in limbo (dispatched but not sent/failed), re-dispatching",
                email_message.id,
            )
        if email_message.send_attempt_failed:
            logger.warning("EmailQueue.send: id=%s is failed, use retry instead", email_message.id)
            return Response(
                {"error": "Cannot send a failed email, use retry instead"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        async_send_email.delay(email_message.id)
        email_message.dispatched = True
        email_message.save(update_fields=["dispatched"])
        logger.info(
            "EmailQueue.send: dispatched id=%s subject='%s' to=%s user=%s",
            email_message.id,
            email_message.subject,
            [r["email"] for r in email_message.recipients],
            request.user,
        )
        return Response({"status": "dispatched", "id": email_message.id})

    @action(detail=False, methods=["post"], url_path="send_all_pending")
    def send_all_pending(self, request):
        """
        Dispatch all pending (sent=False, dispatched=False, send_attempt_failed=False)
        emails to Celery for sending.
        """
        pending = models.EmailMessage.objects.filter(
            sent=False, send_attempt_failed=False
        )
        ids = list(pending.values_list("id", flat=True))
        for email_id in ids:
            async_send_email.delay(email_id)
        pending.update(dispatched=True)
        logger.info(
            "EmailQueue.send_all_pending: dispatched %s emails ids=%s user=%s",
            len(ids),
            ids,
            request.user,
        )
        return Response({"status": "dispatched", "count": len(ids)})

    @action(detail=True, methods=["post"], url_path="resend")
    def resend(self, request, pk=None):
        """
        Clone a sent email and dispatch the clone.
        Only sent emails can be resent.
        """
        original = self.get_object()
        if not original.sent:
            return Response(
                {"error": "Only sent emails can be resent"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if original.send_attempt_failed:
            return Response(
                {"error": "Cannot resend a failed email, use retry instead"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cloned = models.EmailMessage.objects.create(
            root_message_id=models.EmailMessage.generate_message_id(
                domain=original.senders[0]["email"].split("@")[1] if original.senders and "@" in original.senders[0].get("email", "") else "localhost"
            ),
            message_id=models.EmailMessage.generate_message_id(
                domain=original.senders[0]["email"].split("@")[1] if original.senders and "@" in original.senders[0].get("email", "") else "localhost"
            ),
            senders=original.senders,
            recipients=original.recipients,
            bcc_recipients=original.bcc_recipients,
            subject=original.subject,
            body=original.body,
            body_html=original.body_html,
            template=original.template,
            attachments=original.attachments,
        )
        async_send_email.delay(cloned.id)
        cloned.dispatched = True
        cloned.save(update_fields=["dispatched"])
        logger.info(
            "EmailQueue.resend: cloned original_id=%s -> new_id=%s subject='%s' to=%s user=%s",
            original.id,
            cloned.id,
            cloned.subject,
            [r["email"] for r in cloned.recipients],
            request.user,
        )
        return Response(
            {"status": "cloned", "id": cloned.id, "original_id": original.id},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="discard")
    def discard(self, request, pk=None):
        """
        Mark a pending email as failed with a user-provided reason.
        """
        email_message = self.get_object()
        if email_message.sent:
            return Response(
                {"error": "Cannot discard an already sent email"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if email_message.send_attempt_failed:
            return Response(
                {"error": "Cannot discard an already failed email"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reason = request.data.get("reason", "cancelado por usuario")
        email_message.send_attempt_failed = True
        email_message.last_error = reason
        email_message.save(update_fields=["send_attempt_failed", "last_error"])
        logger.info(
            "EmailQueue.discard: id=%s marked as failed reason='%s' user=%s",
            email_message.id,
            reason,
            request.user,
        )
        return Response({"status": "discarded", "id": email_message.id})

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, request, pk=None):
        """
        Clone a failed email and dispatch the clone.
        Marks the original as retried so it cannot be retried again.
        """
        original = self.get_object()
        if not original.send_attempt_failed:
            return Response(
                {"error": "Only failed emails can be retried"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if original.retried:
            return Response(
                {"error": "This email was already retried"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        domain = (
            original.senders[0]["email"].split("@")[1]
            if original.senders and "@" in original.senders[0].get("email", "")
            else "localhost"
        )

        cloned = models.EmailMessage.objects.create(
            root_message_id=models.EmailMessage.generate_message_id(domain=domain),
            message_id=models.EmailMessage.generate_message_id(domain=domain),
            senders=original.senders,
            recipients=original.recipients,
            bcc_recipients=original.bcc_recipients,
            subject=original.subject,
            body=original.body,
            body_html=original.body_html,
            template=original.template,
            attachments=original.attachments,
        )

        async_send_email.delay(cloned.id)
        cloned.dispatched = True
        cloned.save(update_fields=["dispatched"])

        original.retried = True
        original.save(update_fields=["retried"])

        logger.info(
            "EmailQueue.retry: original_id=%s cloned_id=%s subject='%s' user=%s",
            original.id,
            cloned.id,
            cloned.subject,
            request.user,
        )
        return Response(
            {"status": "retried", "id": cloned.id, "original_id": original.id},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """
        Queue statistics for the frontend.
        """
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return Response({
            "pending": models.EmailMessage.objects.filter(
                sent=False, dispatched=False, send_attempt_failed=False
            ).count(),
            "sent_today": models.EmailMessage.objects.filter(
                sent=True, date__gte=today
            ).count(),
            "sent_total": models.EmailMessage.objects.filter(
                sent=True
            ).count(),
            "failed": models.EmailMessage.objects.filter(
                send_attempt_failed=True
            ).count(),
            "total": models.EmailMessage.objects.count(),
            "auto_send": config.EMAIL_AUTO_SEND,
        })

    @action(detail=True, methods=["get"], url_path="body")
    def get_body(self, request, pk=None):
        email_message = self.get_object()
        return Response({
            "id": email_message.id,
            "body": email_message.body,
            "body_html": email_message.body_html,
        })

    @action(detail=True, methods=["get"], url_path="failmsg")
    def get_failmsg(self, request, pk=None):
        email_message = self.get_object()
        return Response({
            "id": email_message.id,
            "send_attempt_failed": email_message.send_attempt_failed,
            "last_error": email_message.last_error,
        })

    @action(detail=False, methods=["post"], url_path="send_email")
    def send_email(self, request):
        """
        Endpoint to send an email.
        """
        try:
            validation = self.validate_params(request)
            if not validation["success"]:
                return Response(
                    {"error": ", ".join(validation["errors"])},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            params = self.build_params(request)
            email_handler = EmailHandler()
            sent_email = email_handler.send_email(**params)

            data = serializers.EmailMessageSerializer(
                sent_email, context={"request": request}
            ).data
            return Response(data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {"error": "There was an error sending the email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def validate_params(self, request):
        """
        Validates send email parameters.
        """
        result = {"success": True, "errors": []}
        in_reply_to = request.data.get("in_reply_to")
        recipients = request.data.get("recipients")
        bcc_recipients = request.data.get("bcc_recipients")
        subject = request.data.get("subject")
        body = request.data.get("body")
        template = request.data.get("template")

        if in_reply_to:
            existing_message = models.EmailMessage.objects.filter(
                id=in_reply_to
            ).first()
            if not existing_message:
                result["success"] = False
                result["errors"].append(
                    "Invalid 'in_reply_to' parameter. "
                    f"Email Message with ID '{in_reply_to}' does not exist."
                )
            else:
                existing_channel = models.CommunicationChannel.objects.filter(
                    message_id=existing_message.root_message_id
                ).first()
                if existing_channel:
                    result["success"] = False
                    result["errors"].append(
                        "Invalid 'in_reply_to' parameter. "
                        f"Email Message with ID '{in_reply_to}' belongs to Communication Channel "
                        f"with ID '{existing_channel.id}'. Please use the Communication Channel"
                    )

        if not recipients and not bcc_recipients and not in_reply_to:
            result["success"] = False
            result["errors"].append("Recipients not provided")

        if not subject and not in_reply_to:
            result["success"] = False
            result["errors"].append("Subject not provided")

        if not body and not template:
            result["success"] = False
            result["errors"].append("Neither Body nor Template provided")

        return result

    def build_params(self, request):
        """
        Builds the parameters for the send email endpoint
        """
        in_reply_to_id = request.data.get("in_reply_to")
        in_reply_to = (
            models.EmailMessage.objects.get(id=in_reply_to_id)
            if in_reply_to_id
            else None
        )
        subject = request.data.get("subject")
        recipients = request.data.get("recipients")
        bcc_recipients = request.data.get("bcc_recipients")
        body = request.data.get("body")
        template = request.data.get("template")
        template_params = request.data.get("template_params")

        return {
            "in_reply_to": in_reply_to,
            "recipients": recipients,
            "bcc_recipients": bcc_recipients,
            "subject": subject,
            "body": body,
            "template": template,
            "template_params": template_params,
        }
