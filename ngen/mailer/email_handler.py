import re
from typing import Union, List, Dict
from django.conf import settings
from ngen.models.email_message import EmailMessage as EmailMessageModel
from ngen.tasks import async_send_email


class EmailHandler:
    """
    Email handler class to send emails
    """

    def __init__(self):
        self.email_sender = settings.CONSTANCE_CONFIG["EMAIL_SENDER"][0]
        self.email_username = settings.CONSTANCE_CONFIG["EMAIL_USERNAME"][0]

    def is_valid_email(self, email: str):
        """
        Method to validate email format.
        """
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_regex, email) is not None

    def validate_and_format_recipients(
        self, recipients, in_reply_to
    ) -> List[Dict[str, str]]:
        """
        Method to validate and format recipients.
        Returns a formatted list of recipients if the provided recipients are valid.
        It concatenates the senders of the in_reply_to email to the recipients if provided.
        It raises a ValueError exception if the provided recipients are not valid.
        """
        if not isinstance(recipients, list):
            raise ValueError("Send email failed. Recipients parameter is not a list.")

        formatted_recipients = in_reply_to.senders if in_reply_to else []

        if all(isinstance(item, str) for item in recipients):
            for email in recipients:
                if not self.is_valid_email(email):
                    raise ValueError(f"Send email failed. Invalid email: '{email}'.")

                if not any(email == sender["email"] for sender in formatted_recipients):
                    formatted_recipients.append(
                        {"name": email.split("@")[0], "email": email}
                    )

            return formatted_recipients

        if all(isinstance(item, dict) for item in recipients):
            for item in recipients:
                if set(item.keys()) != {"name", "email"}:
                    raise ValueError(
                        f"Send email failed. Invalid recipient keys: '{item.keys()}'."
                    )
                if not isinstance(item["name"], str) or not isinstance(
                    item["email"], str
                ):
                    raise ValueError(
                        f"Send email failed. Invalid recipient format, '{item}' is not a string."
                    )
                if not self.is_valid_email(item["email"]):
                    raise ValueError(
                        f"Send email failed. Invalid recipient email format: '{item['email']}'."
                    )
                if not any(
                    item["email"] == sender["email"] for sender in formatted_recipients
                ):
                    formatted_recipients.append(item)

            return formatted_recipients

        raise ValueError("Send email failed. Invalid recipients format")

    def send_email(
        self,
        recipients: Union[List[str], List[Dict[str, str]]],
        subject: str,
        body: str,
        in_reply_to: EmailMessageModel = None,
    ):
        """
        Method to send emails.

        :param Union[List[int], Dict[str, int]] recipients: list of recipients.
        (optional if "in_reply_to" parameter is provided)
        Valid format examples:
            1) ["admin@info.unlp.edu.ar"]
            2) [{"name": "University Administrator", "email": "admin@info.unlp.edu.ar"}]

        :param str subject: email subject
        :param str body: email body
        :param EmailMessage in_reply_to: email to reply (optional)
        :return EmailMessage: Email message that was sent
        """

        if not recipients and not in_reply_to:
            raise ValueError("Send email failed. Recipients not provided")

        if not subject:
            raise ValueError("Send email failed. Subject not provided")

        if not body:
            raise ValueError("Send email failed. Body not provided")

        if in_reply_to and not isinstance(in_reply_to, EmailMessageModel):
            raise ValueError("Send email failed. in_reply_to must be an EmailMessage")

        recipients = self.validate_and_format_recipients(recipients, in_reply_to)

        message_id = EmailMessageModel.generate_message_id(
            domain=self.email_sender.split("@")[1]
        )

        if in_reply_to:
            subject = in_reply_to.subject
            if not subject.startswith("Re: "):
                subject = f"Re: {subject}"

        email_message = EmailMessageModel.objects.create(
            root_message_id=in_reply_to.root_message_id if in_reply_to else message_id,
            parent_message_id=in_reply_to.message_id if in_reply_to else None,
            references=(
                in_reply_to.references + [in_reply_to.message_id] if in_reply_to else []
            ),
            message_id=message_id,
            senders=[{"name": self.email_username, "email": self.email_sender}],
            recipients=recipients,
            subject=subject,
            body=body,
        )

        async_send_email.delay(email_message.id)

        return email_message
