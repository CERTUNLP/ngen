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
    status = django_filters.MultipleChoiceFilter(
        choices=models.EmailMessage.Status.choices
    )

    class Meta:
        model = models.EmailMessage
        fields = ["status"]


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
        email_message = self.get_object()
        if email_message.status == models.EmailMessage.Status.SENT:
            logger.warning("EmailQueue.send: id=%s already sent, skipping", email_message.id)
            return Response(
                {"error": "Email already sent"}, status=status.HTTP_400_BAD_REQUEST
            )
        if email_message.status not in (models.EmailMessage.Status.PENDING, models.EmailMessage.Status.CANCELLED):
            logger.warning(
                "EmailQueue.send: id=%s is already dispatched (status=%s), skipping",
                email_message.id,
                email_message.status,
            )
            return Response(
                {"error": "Email already dispatched to Celery"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email_message.status = models.EmailMessage.Status.SENDING
        email_message.save(update_fields=["status"])
        async_send_email.delay(email_message.id)
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
        pending = models.EmailMessage.objects.filter(
            status=models.EmailMessage.Status.PENDING
        )
        ids = list(pending.values_list("id", flat=True))
        pending.update(status=models.EmailMessage.Status.SENDING)
        for email_id in ids:
            async_send_email.delay(email_id)
        logger.info(
            "EmailQueue.send_all_pending: dispatched %s emails ids=%s user=%s",
            len(ids),
            ids,
            request.user,
        )
        return Response({"status": "dispatched", "count": len(ids)})

    @action(detail=True, methods=["post"], url_path="resend")
    def resend(self, request, pk=None):
        original = self.get_object()
        if original.status not in (
            models.EmailMessage.Status.SENT,
            models.EmailMessage.Status.CANCELLED,
        ):
            return Response(
                {"error": "Only sent or cancelled emails can be resent"},
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
        cloned.status = models.EmailMessage.Status.SENDING
        cloned.save(update_fields=["status"])
        async_send_email.delay(cloned.id)
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
        email_message = self.get_object()
        if email_message.status == models.EmailMessage.Status.SENT:
            return Response(
                {"error": "Cannot discard an already sent email"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if email_message.status == models.EmailMessage.Status.FAILED:
            return Response(
                {"error": "Cannot discard an already failed email"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if email_message.status == models.EmailMessage.Status.CANCELLED:
            return Response(
                {"error": "Email already discarded"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reason = request.data.get("reason", "cancelado por usuario")
        email_message.status = models.EmailMessage.Status.CANCELLED
        email_message.last_error = reason
        email_message.save(update_fields=["status", "last_error"])
        logger.info(
            "EmailQueue.discard: id=%s cancelled reason='%s' user=%s",
            email_message.id,
            reason,
            request.user,
        )
        return Response({"status": "discarded", "id": email_message.id})

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_dispatched(self, request, pk=None):
        email_message = self.get_object()
        if email_message.status not in (
            models.EmailMessage.Status.SENDING,
            models.EmailMessage.Status.RETRYING,
        ):
            return Response(
                {"error": "Only dispatched emails can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email_message.status = models.EmailMessage.Status.CANCELLED
        email_message.save(update_fields=["status"])
        logger.info(
            "EmailQueue.cancel: id=%s cancelled by user=%s",
            email_message.id,
            request.user,
        )
        return Response({"status": "cancelled", "id": email_message.id})

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, request, pk=None):
        original = self.get_object()
        if original.status != models.EmailMessage.Status.FAILED:
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

        cloned.status = models.EmailMessage.Status.SENDING
        cloned.save(update_fields=["status"])
        async_send_email.delay(cloned.id)

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
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return Response({
            "pending": models.EmailMessage.objects.filter(
                status=models.EmailMessage.Status.PENDING
            ).count(),
            "dispatched": models.EmailMessage.objects.filter(
                status__in=(models.EmailMessage.Status.SENDING, models.EmailMessage.Status.RETRYING)
            ).count(),
            "sent_today": models.EmailMessage.objects.filter(
                status=models.EmailMessage.Status.SENT, date__gte=today
            ).count(),
            "sent_total": models.EmailMessage.objects.filter(
                status=models.EmailMessage.Status.SENT
            ).count(),
            "failed": models.EmailMessage.objects.filter(
                status=models.EmailMessage.Status.FAILED
            ).count(),
            "cancelled": models.EmailMessage.objects.filter(
                status=models.EmailMessage.Status.CANCELLED
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
            "status": email_message.status,
            "last_error": email_message.last_error,
        })

    @action(detail=False, methods=["post"], url_path="send_email")
    def send_email(self, request):
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
