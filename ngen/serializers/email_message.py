from ngen import models
from rest_framework import serializers


class EmailMessageListSerializer(serializers.ModelSerializer):
    attachment_count = serializers.SerializerMethodField()
    recipient_count = serializers.SerializerMethodField()

    class Meta:
        model = models.EmailMessage
        fields = [
            "id",
            "created",
            "modified",
            "root_message_id",
            "parent_message_id",
            "message_id",
            "references",
            "senders",
            "recipients",
            "bcc_recipients",
            "subject",
            "date",
            "status",
            "template",
            "attachments",
            "size",
            "retried",
            "retry_count",
            "attachment_count",
            "recipient_count",
        ]

    def get_attachment_count(self, obj):
        return len(obj.attachments or [])

    def get_recipient_count(self, obj):
        return len(obj.recipients or [])


class EmailMessageSerializer(EmailMessageListSerializer):
    class Meta(EmailMessageListSerializer.Meta):
        fields = EmailMessageListSerializer.Meta.fields + [
            "body",
            "body_html",
            "last_error",
        ]
