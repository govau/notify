from cachelib import SimpleCache
from app.clients.sms.utils import timed
from saplivelink365 import Configuration, ApiClient, AuthorizationApi, SMSV20Api

# See https://livelink.sapmobileservices.com/documentation/guides/sms-channel/delivery_statuses/#body-description
sap_response_map = {
    'SENT': 'sending',
    'DELIVERED': 'delivered',
    'RECEIVED': 'delivered',
    'ERROR': 'permanent-failure',
}

auth_cache = SimpleCache()


def get_sap_responses(status):
    return sap_response_map[status]


class SAPSMSClient:
    def __init__(self, client_id=None, client_secret=None, *args, **kwargs):
        super(SAPSMSClient, self).__init__(*args, **kwargs)
        self._client_id = client_id
        self._client_secret = client_secret

    def init_app(self, logger, notify_host, *args, **kwargs):
        self.logger = logger
        self.notify_host = notify_host

    @property
    def name(self):
        return 'sap'

    @property
    def _client(self):
        return ApiClient(self.with_auth_config)

    def get_name(self):
        return self.name

    @timed("SAP send SMS request")
    def send_sms(self, to, content, reference, sender=None):
        sms_api = SMSV20Api(self._client)

        from app.sap.oauth2 import OAuth2Client
        oauth2_client = OAuth2Client.query.first()

        callback = [
            {
                "url": f"{self.notify_host}/notifications/sms/sap/{reference}",
                "authType": "OAUTH2",
                "oAuth2": {
                    "oAuthClient": oauth2_client.client_id,
                    "oAuthSecret": oauth2_client.client_secret,
                    "tokenUrl": f"{self.notify_host}/sap/oauth2/token"
                }
            }
        ] if self.notify_host and oauth2_client else None

        body = {
            "origin": sender if sender else None,
            "destination": [
                to
            ],
            "message": content,
            "callback": callback,
            "acknowledgement": True,
            "ackType": "MESSAGE",
            "subject": reference
        }

        try:
            resp = sms_api.send_sms_using_post(body=body)
            order = resp.livelink_order_ids[0]
            self.logger.info(f"SAP send SMS request for {reference} succeeded: {order.livelink_order_id[0]}")

            # Avoid circular imports by importing this file later.
            from app.models import (
                NOTIFICATION_SENDING
            )
            return order.livelink_order_id[0], NOTIFICATION_SENDING
        except Exception as e:
            self.logger.error(f"SAP send SMS request for {reference} failed")
            raise e

    @property
    @timed("SAP auth request")
    def with_auth_config(self):
        key = 'auth'
        access_token = auth_cache.get(key)

        if access_token is None:
            auth_api = AuthorizationApi(ApiClient(Configuration(
                username=self._client_id,
                password=self._client_secret,
            )))

            resp = auth_api.token_authorization_using_post1('client_credentials')

            access_token = resp.access_token

            auth_cache.set(key, access_token, timeout=30 * 60)  # 30 minutes (token is valid for 45 minutes)

        conf = Configuration()
        conf.access_token = access_token

        return conf
