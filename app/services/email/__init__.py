from typing import Optional, Dict, Any, List, Union

from flask import current_app, render_template
from flask_mail import Message

from app import mail, logger


def send_email(
    to: str,
    subject: str,
    template: str,
    sender: Optional[Union[str, tuple]] = None,
    reply_to: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[tuple]] = None,
    **kwargs: Dict[str, Any]
) -> bool:
    """
    Send an email using Flask-Mail.

    Args:
        to (str): Recipient email address.
        subject (str): Email subject.
        template (str): Template name (without file extension).
        sender (Optional[Union[str, tuple]], optional): Sender email address or (name, email).
            Defaults to the configured `MAIL_DEFAULT_SENDER`.
        reply_to (Optional[str], optional): Reply-to email address.
        cc (Optional[List[str]], optional): List of CC recipients.
        bcc (Optional[List[str]], optional): List of BCC recipients.
        attachments (Optional[List[tuple]], optional): Attachments in (filename, content, content_type) format.
        **kwargs (Dict[str, Any]): Additional template variables.

    Returns:
        bool: True if the email was successfully sent, False otherwise.
    """
    try:
        config = current_app.config
        testing_mode = config.get("TESTING", False)

        # Enforce admin email in testing mode
        recipient_email = config.get("ADMIN_EMAIL") if testing_mode else to

        # Enforce default sender from config
        sender = sender or config.get("MAIL_DEFAULT_SENDER")
        if not sender:
            logger.error("MAIL_DEFAULT_SENDER is not configured.")
            return False

        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            sender=sender,
            cc=cc or [],
            bcc=bcc or []
        )

        if reply_to:
            msg.reply_to = reply_to

        # Render email templates
        msg.body = render_template(f"{template}.txt", **kwargs)
        msg.html = render_template(f"{template}.html", **kwargs)

        # Add attachments if provided
        if attachments:
            for filename, content, content_type in attachments:
                msg.attach(filename, content_type, content)

        # Log email details in testing mode instead of sending
        if testing_mode:
            logger.info(f"[TEST MODE] Email to {recipient_email} (Subject: {subject}) not sent.")
            return True

        # Send the email
        mail.send(msg)
        return True

    except Exception as err:
        logger.error(f"Email send failed: {err}")
        return False
