import django_filters
from rest_framework import permissions, filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ngen import models, serializers
from ngen.mailer.email_handler import EmailHandler


class EmailMessageViewSet(viewsets.ModelViewSet):
    """
    EmailMessage viewset.
    """

    queryset = models.EmailMessage.objects.all().order_by("id")
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    ordering_fields = ["id", "created", "modified", "date"]
    serializer_class = serializers.EmailMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

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

        if not recipients:
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
        in_reply_to = request.data.get("in_reply_to")
        subject = request.data.get("subject")
        body = request.data.get("body")
        template = request.data.get("template")
        template_params = request.data.get("template_params")

        return {
            "in_reply_to": (
                models.EmailMessage.objects.get(id=in_reply_to) if in_reply_to else None
            ),
            "recipients": request.data.get("recipients"),
            "subject": subject,
            "body": body,
            "template": template,
            "template_params": template_params,
        }
