import smtplib
import uuid
from email.message import EmailMessage


class SMTPClient:
    def __init__(
            self,
            addr=None,
            port=587,
            user=None,
            password=None):
        self._addr = addr
        self._port = port
        self._user = user
        self._password = password

    def init_app(self, application, statsd_client, *args, **kwargs):
        super(SMTPClient, self).__init__(*args, **kwargs)
        self.statsd_client = statsd_client

    @property
    def name(self):
        return 'smtp'

    def get_name(self):
        return self.name

    def send_email(
            self,
            source,
            to_addresses,
            subject,
            body,
            html_body='',
            reply_to_address=None):
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]

        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = source
        message['To'] = ", ".join(to_addresses)
        if reply_to_address:
            message['Reply-to'] = reply_to_address

        message.set_content(body)
        if html_body:
            message.add_alternative(html_body, subtype='html')

        reference = uuid.uuid4()

        # This block might throw which will result in the send being retryed up
        # to max_retries. We won't catch any specific exceptions here which
        # map to permanent failures, although this could be enhanced to do so.
        # In such a scenario, this method should return the corresponding
        # failure status (e.g. NOTIFICATION_PERMANENT_FAILURE).
        with smtplib.SMTP(self._addr, self._port) as server:
            server.starttls()
            server.login(self._user, self._password)
            server.send_message(message)

        # Avoid circular imports by importing this file later.
        from app.models import (
            NOTIFICATION_SENT
        )

        # If we reach this point, the email has been sent. It may not actually
        # be delivered. E.g. this doesn't account for cases such as the
        # recipient's server rejecting the message. All we know is that the SMTP
        # server said it was sent.
        return reference, NOTIFICATION_SENT
