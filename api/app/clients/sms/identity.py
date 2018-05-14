from requests import request, RequestException
from app.clients.sms import SmsClient

class IdentitySMSClient(SmsClient):
    def __init__(self, addr=None, user=None, password=None, *args, **kwargs):
        super(IdentitySMSClient, self).__init__(*args, **kwargs)
        self._addr = addr
        self._user = user
        self._password = password

    def init_app(self, app, *args, **kwargs):
        self.current_app = app

    @property
    def name(self):
        return 'identity'

    def get_name(self):
        return self.name

    def record_outcome(self, response):
        success = response.ok and not response.json().get('error')

        log_message = "API {} request {} on {} response status_code {}".format(
            "POST",
            "succeeded" if success else "failed",
            self._addr,
            response.status_code
        )

        if success:
            self.current_app.logger.info(log_message)
        else:
            self.current_app.logger.error(log_message)

    def send_sms(self, to, content, reference, sender=None):
        data = {
            "mobileNumber": to,
            "message": content,
        }

        response = request(
            'POST',
            '{addr}{path}'.format(
                addr=self._addr,
                path='/api/v1/sendsms'
            ),
            json=data,
            auth=(self._user, self._password)
        )
        response.raise_for_status()
        self.record_outcome(response)
        return response
