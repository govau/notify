from monotonic import monotonic
from app.clients.sms import SmsClient
import Telstra_Messaging

telstra_response_map = {
    'PEND': 'pending',
    'SENT': 'sending',
    'DELIVRD': 'delivered',
    'EXPIRED': 'permanent-failure',  # TODO: assuming this is permanent
    'DELETED': 'permanent-failure',  # TODO: assuming this is permanent
    'UNDVBL': 'permanent-failure',  # TODO: assuming this is permanent
    'REJECTED': 'temporary-failure',  # TODO: assuming this is temporary
    'READ': 'delivered'  # TODO: can we add a new status 'read'?
}


def get_telstra_responses(status):
    return telstra_response_map[status]


class TelstraSMSClient(SmsClient):
    def __init__(self, client_id=None, client_secret=None, *args, **kwargs):
        super(TelstraSMSClient, self).__init__(*args, **kwargs)
        self._client_id = client_id
        self._client_secret = client_secret

    def init_app(self, logger, callback_notify_url_host, *args, **kwargs):
        self.logger = logger
        self._callback_notify_url_host = callback_notify_url_host

    @property
    def name(self):
        return 'telstra'

    def get_name(self):
        return self.name

    def send_sms(self, to, content, reference, sender=None):
        conf = self.auth()

        api_instance = Telstra_Messaging.MessagingApi(Telstra_Messaging.ApiClient(conf))
        payload = Telstra_Messaging.SendSMSRequest(
            to=to,
            body=content,
            notify_url="{}/notifications/sms/telstra/{}".format(self._callback_notify_url_host, reference)
        )

        start_time = monotonic()
        try:
            resp = api_instance.send_sms(payload)
            self.logger.info("Telstra send SMS request for {} succeeded: {}".format(reference, resp))
        except Exception as e:
            self.logger.error("Telstra send SMS request for {} failed".format(reference))
            raise e
        finally:
            elapsed_time = monotonic() - start_time
            self.logger.info("Telstra send SMS request for {} finished in {}".format(reference, elapsed_time))

    def auth(self):
        grant_type = 'client_credentials'

        api_instance = Telstra_Messaging.AuthenticationApi()

        start_time = monotonic()
        try:
            resp = api_instance.auth_token(self._client_id, self._client_secret, grant_type)

            self.logger.info("Telstra auth request succeeded")

            conf = Telstra_Messaging.Configuration()
            conf.access_token = resp.access_token

            return conf
        except Exception as e:
            self.logger.error("Telstra auth request failed")
            raise e
        finally:
            elapsed_time = monotonic() - start_time
            self.logger.info("Telstra auth request finished in {}".format(elapsed_time))
