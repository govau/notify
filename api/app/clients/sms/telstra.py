from monotonic import monotonic
import json
from app.clients.sms import SmsClient
import Telstra_Messaging
from Telstra_Messaging.rest import ApiException

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
    def __init__(self, notify_service_client_id=None, notify_service_client_secret=None, client_id=None, client_secret=None, *args, **kwargs):
        super(TelstraSMSClient, self).__init__(*args, **kwargs)
        self._notify_service_client_id = notify_service_client_id
        self._notify_service_client_secret = notify_service_client_secret
        self._client_id = client_id
        self._client_secret = client_secret

    def init_app(self, logger, notify_service_id, callback_notify_url_host, *args, **kwargs):
        self.logger = logger
        self._notify_service_id = notify_service_id
        self._callback_notify_url_host = callback_notify_url_host

    @property
    def name(self):
        return 'telstra'

    def get_name(self):
        return self.name

    def send_sms(self, to, content, reference, sender=None, service_id=None):
        auth_conf = self.auth(service_id)

        api_instance = Telstra_Messaging.MessagingApi(Telstra_Messaging.ApiClient(auth_conf))
        req = Telstra_Messaging.SendSMSRequest(
            to=to,
            body=content,
            notify_url="{}/notifications/sms/telstra/{}".format(self._callback_notify_url_host, reference) if self._callback_notify_url_host else ""
        )

        start_time = monotonic()
        try:
            resp = api_instance.send_sms(req)
            message = resp.messages[0]
            self.logger.info("Telstra send SMS request for {} succeeded: {}".format(reference, message.message_id))
        except ApiException as e:
            self.logger.error("Telstra send SMS request for {} failed".format(reference))

            if e.status != 400:
                raise e

            json_resp = json.loads(e.body)
            if json_resp['code'] != 'NOT-PROVISIONED':
                raise e

            self.logger.error("Telstra subscription is not provisioned, will do that now")
            self.provision_subscription(auth_conf)

            # Now rethrow the original exception so that sending is retryed.
            raise e
        except Exception as e:
            self.logger.error("Telstra send SMS request for {} failed".format(reference))
            raise e
        finally:
            elapsed_time = monotonic() - start_time
            self.logger.info("Telstra send SMS request for {} finished in {}".format(reference, elapsed_time))

    def provision_subscription(self, auth_conf):
        api_instance = Telstra_Messaging.ProvisioningApi(Telstra_Messaging.ApiClient(auth_conf))

        start_time = monotonic()
        try:
            req = Telstra_Messaging.ProvisionNumberRequest(
                active_days=30  # TODO: max we can do for trial Telstra accounts
            )
            resp = api_instance.create_subscription(req)

            self.logger.info("Telstra provision request succeeded: {}".format(json.dumps(resp)))
        except Exception as e:
            self.logger.error("Telstra provision request failed")
            raise e
        finally:
            elapsed_time = monotonic() - start_time
            self.logger.info("Telstra provision request finished in {}".format(elapsed_time))

    def auth(self, service_id=None):
        grant_type = 'client_credentials'

        api_instance = Telstra_Messaging.AuthenticationApi()

        start_time = monotonic()
        try:
            client_id = self._client_id
            client_secret = self._client_secret

            # The Notify system service uses a different Telstra application.
            if service_id == self._notify_service_id:
                self.logger.info("Using Notify system Telstra credentials")

                client_id = self._notify_service_client_id
                client_secret = self._notify_service_client_secret

            resp = api_instance.auth_token(client_id, client_secret, grant_type)

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
