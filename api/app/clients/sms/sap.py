import datetime
from cachelib import SimpleCache
from app.clients.sms import PollableSMSClient
from app.clients.sms.utils import timed
from saplivelink365 import Configuration, ApiClient, AuthorizationApi, SMSV20Api, ApiException

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


class SAPSMSClient(PollableSMSClient):
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

    # https://livelink.sapmobileservices.com/documentation/guides/sms-channel/delivery_statuses/#pulling-acks
    def query_sms_statuses(self, reference, start_time, end_time):
        # SAP expects yyyyMMddHHmm
        fmt_string = '%Y%m%d%H%M'
        start_utc_time = int(start_time.strftime(fmt_string))
        end_utc_time = int(end_time.strftime(fmt_string))

        page_index = 0
        page_count = 1
        sms_api = SMSV20Api(self._client)

        while page_index < page_count:
            response = sms_api.query_status_using_get1(
                order_id=reference,
                status='DELIVERED',
                page_index=page_index + 1,
                start_utc_time=start_utc_time,
                end_utc_time=end_utc_time
            )
            page_index = response.page_index
            page_count = response.page_count
            for message in response.sap_notification:
                yield message.order_id, message.status

        self.logger.info(f"SAP query for SMS status scanned {page_count} pages")

    @timed("SAP get message status request")
    def check_message_status(self, reference, sent_at=None, **options):
        jitter = datetime.timedelta(hours=12)

        if not sent_at:
            return

        start_time = sent_at - jitter
        end_time = sent_at + jitter

        yield from self.query_sms_statuses(reference, start_time, end_time)

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
        except ApiException as e:
            if e.status == 401:
                key = 'auth'
                access_token = None
                auth_cache.set(key, access_token)
                raise e
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
