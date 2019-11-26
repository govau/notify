from app.clients.sms.utils import timed
import Telstra_Messaging as telstra

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


class TelstraSMSClient:
    def __init__(self, client_id=None, client_secret=None, *args, **kwargs):
        super(TelstraSMSClient, self).__init__(*args, **kwargs)
        self._client_id = client_id
        self._client_secret = client_secret

    def init_app(self, logger, notify_host, *args, **kwargs):
        self.logger = logger
        self.notify_host = notify_host

    @property
    def name(self):
        return 'telstra'

    @property
    def _client(self):
        return telstra.ApiClient(self.auth)

    def get_name(self):
        return self.name

    # https://dev.telstra.com/content/messaging-api#operation/Send%20SMS
    @timed("Telstra send SMS request")
    def send_sms(self, to, content, reference, sender=None):
        telstra_api = telstra.MessagingApi(self._client)
        notify_url = f"{self.notify_host}/notifications/sms/telstra/{reference}" if self.notify_host else None

        payload = telstra.SendSMSRequest(
            to=to,
            body=content,
            _from=sender if sender else None,
            notify_url=notify_url
        )

        try:
            resp = telstra_api.send_sms(payload)
            message = resp.messages[0]
            self.logger.info(f"Telstra send SMS request for {reference} succeeded: {message.message_id}")

        except Exception as e:
            self.logger.error(f"Telstra send SMS request for {reference} failed")
            raise e

    @timed("Telstra provision request")
    def provision_subscription(self):
        # maximum subscription is 5 years, 1825 days
        telstra_api = telstra.ProvisioningApi(self._client)
        req = telstra.ProvisionNumberRequest(active_days=1825)
        telstra_api.create_subscription(req)

    # https://dev.telstra.com/content/messaging-api#operation/Get%20SMS%20Status
    @timed("Telstra get message status request")
    def get_message_status(self, message_id):
        telstra_api = telstra.MessagingApi(self._client)
        return telstra_api.get_sms_status(message_id=message_id)

    # TODO: cache this call. token is valid for 1 hr.
    # https://dev.telstra.com/content/messaging-api#tag/Authentication
    @property
    @timed("Telstra auth request")
    def auth(self):
        grant_type = 'client_credentials'
        api_instance = telstra.AuthenticationApi()

        resp = api_instance.auth_token(self._client_id, self._client_secret, grant_type)
        conf = telstra.Configuration()
        conf.access_token = resp.access_token
        return conf
