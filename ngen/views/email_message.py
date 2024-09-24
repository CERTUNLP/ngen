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
            self.validate_in_reply_to_param(request)
            self.validate_communication_channel_param(request)
            email_handler = EmailHandler()
            sent_email = email_handler.send_email(
                recipients=request.data.get("recipients"),
                subject=request.data.get("subject"),
                body=request.data.get("body"),
                in_reply_to=(
                    models.EmailMessage.objects.get(id=request.data.get("in_reply_to"))
                    if request.data.get("in_reply_to")
                    else None
                ),
            )
            self.handle_communication_channel_param(request, sent_email)

            data = serializers.EmailMessageSerializer(
                sent_email, context={"request": request}
            ).data
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def validate_in_reply_to_param(self, request):
        """
        Validates the in_reply_to parameter, if provided.
        """
        in_reply_to = request.data.get("in_reply_to")
        if in_reply_to and not models.EmailMessage.objects.filter(id=in_reply_to):
            raise ValueError(
                "Invalid 'in_reply_to' parameter. "
                f"Email Message with ID '{in_reply_to}' does not exist."
                ""
            )

    def validate_communication_channel_param(self, request):
        """
        Validates the communication_channel_id parameter, if provided.
        """
        if request.data.get("in_reply_to"):
            return

        communication_channel_id = request.data.get("communication_channel_id")
        if communication_channel_id and not models.CommunicationChannel.objects.filter(
            id=communication_channel_id
        ):
            raise ValueError(
                "Invalid 'communication_channel_id' parameter. "
                f"Communication Channel with ID '{communication_channel_id}' does not exist."
            )

    def handle_communication_channel_param(self, request, sent_email):
        """
        If communication_channel_id parameter is provided and the email is not a reply,
        associates the sent email with the provided communication channel.
        """
        if request.data.get("in_reply_to"):
            return

        communication_channel_id = request.data.get("communication_channel_id")
        if communication_channel_id:
            communication_channel = models.CommunicationChannel.objects.get(
                id=communication_channel_id
            )
            communication_channel.message_id = sent_email.message_id
            communication_channel.save()
