import re
from typing import Optional, Union, List, Dict
from constance import config

from ngen.models.email_message import EmailMessage as EmailMessageModel
from ngen.utils import clean_list
from ngen.models.announcement import Communication


EMAIL_TEMPLATES = {
    "case_report": "reports/case_report.html",
    "case_closed_report": "reports/case_closed_report.html",
    "case_change_state": "reports/case_change_state.html",
}


class EmailHandler:
    """
    Email handler class to send emails
    """

    def __init__(self):
        self.email_sender = config.EMAIL_SENDER
        self.email_username = config.EMAIL_USERNAME

        if not self.email_sender:
            raise ValueError("EMAIL_SENDER not configured")

        if not self.email_username:
            raise ValueError("EMAIL_USERNAME not configured")

    def is_valid_email(self, email: str):
        """
        Method to validate email format.
        """
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_regex, email) is not None

    def validate_and_format_recipients(
        self, recipients, in_reply_to, bcc=False
    ) -> List[Dict[str, str]]:
        """
        Method to validate and format recipients.
        Returns a formatted list of recipients.
        Concatenates the senders of the in_reply_to email to the recipients, if provided.
        Concatenates the recipients of the in_reply_to email to the recipients,
        if provided, excluding the app email.
        Raises a ValueError exception if the provided recipients are not valid.

        :param recipients: list of recipients
        :param in_reply_to: EmailMessage to reply
        :param bcc: boolean indicating if recipients are bcc recipients, default is False
        """

        formatted_recipients = []

        if in_reply_to:
            # Add sender of the email being replied to
            formatted_recipients.extend(in_reply_to.senders)

            if bcc:
                # Add the bcc recipients of the email being replied to
                # Example: when replying to an email sent by the app with bcc recipients
                formatted_recipients.extend(in_reply_to.bcc_recipients)
            else:
                # Add the recipients of the email being replied to
                formatted_recipients.extend(in_reply_to.recipients)

        # Remove app email from recipients
        formatted_recipients = [
            recipient
            for recipient in formatted_recipients
            if recipient["email"] != self.email_sender
        ]

        if not recipients:
            return formatted_recipients

        if not isinstance(recipients, list):
            raise ValueError("Send email failed. Recipients parameter is not a list.")

        recipients = clean_list(recipients)

        # If recipients is a list of strings
        if all(isinstance(item, str) for item in recipients):
            for email in recipients:
                # If email is not valid
                if not self.is_valid_email(email):
                    raise ValueError(f"Send email failed. Invalid email: '{email}'.")

                # If email is not already in the formatted recipients
                if not any(
                    email == recipient["email"] for recipient in formatted_recipients
                ):
                    formatted_recipients.append(
                        {"name": email.split("@")[0], "email": email}
                    )

            return formatted_recipients

        # If recipients is a list of dictionaries
        if all(isinstance(item, dict) for item in recipients):
            for item in recipients:
                # If recipient does not have 'name' and 'email' keys
                if set(item.keys()) != {"name", "email"}:
                    raise ValueError(
                        "Send email failed. Invalid recipient keys. "
                        "Recipients must have 'name' and 'email' keys."
                    )

                # If recipient name or email are not a string
                if not isinstance(item["name"], str) or not isinstance(
                    item["email"], str
                ):
                    raise ValueError(
                        f"Send email failed. Invalid recipient format, '{item}' is not a string."
                    )

                # If recipient email is not valid
                if not self.is_valid_email(item["email"]):
                    raise ValueError(
                        f"Send email failed. Invalid recipient email format: '{item['email']}'."
                    )

                # If email is not already in the formatted recipients
                if not any(
                    item["email"] == sender["email"] for sender in formatted_recipients
                ):
                    formatted_recipients.append(item)

            return formatted_recipients

        raise ValueError("Send email failed. Invalid recipients format")

    def send_email(
        self,
        recipients: Union[List[str], List[Dict[str, str]]] = None,
        bcc_recipients: Union[List[str], List[Dict[str, str]]] = None,
        subject: str = None,
        body: Optional[str] = None,
        template: Optional[str] = None,
        template_params: Optional[dict] = None,
        in_reply_to: EmailMessageModel = None,
        attachments: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Method to send emails.

        :param Union[List[str], Dict[str, str]] recipients: list of recipients.
        (optional if "in_reply_to" parameter is provided)
        Valid format examples:
            1) ["admin@info.unlp.edu.ar"]
            2) [{"name": "University Administrator", "email": "admin@info.unlp.edu.ar"}]

        :param Union[List[str], Dict[str, str]] bcc_recipients: list of bcc recipients.
        Same format as recipients.
        :param str subject: email subject
        :param str body: email body
        :param str template: path of the email template
        :param dict template_params: template parameters.
         Will be used if template is provided and the message is not associated
         with a channelable (through a Communication Channel).
        :param EmailMessage in_reply_to: email to reply (optional)
        :return EmailMessage: Email message that was sent
        """

        if not recipients and not bcc_recipients and not in_reply_to:
            raise ValueError("Send email failed. Recipients not provided")

        if not subject and not in_reply_to:
            raise ValueError("Send email failed. Subject not provided")

        if not body and not template:
            raise ValueError("Send email failed. Neither Body nor Template provided.")

        if template and template not in EMAIL_TEMPLATES:
            raise ValueError("Send email failed. Invalid template")

        rendered_template = {}
        if template:
            rendered_template = Communication.render_template(
                EMAIL_TEMPLATES[template], extra_params=template_params
            )

        if in_reply_to and not isinstance(in_reply_to, EmailMessageModel):
            raise ValueError("Send email failed. in_reply_to must be an EmailMessage")

        recipients = self.validate_and_format_recipients(recipients, in_reply_to)

        bcc_recipients = self.validate_and_format_recipients(
            bcc_recipients, in_reply_to, bcc=True
        )

        message_id = EmailMessageModel.generate_message_id(
            domain=self.email_sender.split("@")[1]
        )

        if in_reply_to:
            subject = in_reply_to.subject
            if not subject.startswith("Re: "):
                subject = f"Re: {subject}"

        # Email is sent asynchronously in post_save signal
        email_message = EmailMessageModel.objects.create(
            root_message_id=in_reply_to.root_message_id if in_reply_to else message_id,
            parent_message_id=in_reply_to.message_id if in_reply_to else None,
            references=(
                in_reply_to.references + [in_reply_to.message_id] if in_reply_to else []
            ),
            message_id=message_id,
            senders=[{"name": self.email_username, "email": self.email_sender}],
            recipients=recipients,
            bcc_recipients=bcc_recipients,
            subject=subject,
            body=body or rendered_template.get("text", ""),
            body_html=rendered_template.get("html", ""),
            template=template,
            template_params=None,
            attachments=attachments if attachments else [],
        )

        return email_message
