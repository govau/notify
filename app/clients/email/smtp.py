import os
import smtplib
from flask import current_app
from email.message import EmailMessage

from app.clients.email import EmailClient


class SMTPClient(EmailClient):
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
        return 'ses'

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

        with smtplib.SMTP(self._addr, self._port) as server:
            server.starttls()
            server.login(self._user, self._password)
            server.send_message(message)

        return 'fake-message-id'
