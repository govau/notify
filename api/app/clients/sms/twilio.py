import random
from monotonic import monotonic
from app.clients.sms import SmsClient
from twilio.rest import Client

# https://www.twilio.com/docs/sms/api/message#sms-status-values
# these are for inbound messages
# 'receiving'
# 'received'
#
# something super frustrating here. We define a 'sent' status in models.py, but
# the text that shows in ui is "Sent internationally". It would make sense to
# map the "sent" status here to "sent", but that ends up showing confusing
# stuff on page.
#
# That's why we map sent -> sending.
twilio_response_map = {
    'accepted': 'created',
    'queued': 'sending',
    'sending': 'sending',
    'sent': 'sending',
    'delivered': 'delivered',
    'undelivered': 'permanent-failure',
    'failed': 'technical-failure',
}


def get_twilio_responses(status):
    return twilio_response_map[status]

class TwilioSMSClient(SmsClient):
    def __init__(self,
            account_sid = None, 
            auth_token = None, 
            from_number = None, 
            *args, **kwargs):
        super(TwilioSMSClient, self).__init__(*args, **kwargs)
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_number = from_number
        self._client = Client(account_sid, auth_token)

    def init_app(self, logger, callback_notify_url_host, *args, **kwargs):
        self.logger = logger
        self._callback_notify_url_host = callback_notify_url_host

    @property
    def name(self):
        return 'twilio'

    def get_name(self):
        return self.name

    def send_sms(self, to, content, reference, sender=None):
        start_time = monotonic()
        from_number = random.choice(self._client.incoming_phone_numbers.list()).phone_number
        callback_url="{}/notifications/sms/twilio/{}".format(self._callback_notify_url_host, reference)
        try:
            message = self._client.messages.create(
                to=to,
                from_=from_number,
                body=content,
                status_callback=callback_url,
            )

            self.logger.info("Twilio send SMS request for {} succeeded: {}".format(reference, message.sid))
        except Exception as e:
            self.logger.error("Twilio send SMS request for {} failed".format(reference))
            raise e
        finally:
            elapsed_time = monotonic() - start_time
            self.logger.info("Twilio send SMS request for {} finished in {}".format(reference, elapsed_time))
