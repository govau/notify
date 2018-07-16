import json
from notifications_python_client.notifications import NotificationsAPIClient

from notifications_python_client.base import BaseAPIClient
from notifications_python_client import __version__

class NotifyAdminAPIClient(NotificationsAPIClient):
    def __init__(self, *args, route_secret = '', **kwargs):
        super().__init__(*args, **kwargs)
        self.service_id = 'notify-admin'
        self.route_secret = route_secret

        self.service_id = 'notify-admin'
        self.api_key = 'dev-notify-secret-key'
        self.route_secret = ''


    def generate_headers(self, *args, **kwargs):
        headers = super().generate_headers(*args, **kwargs)
        headers['X-Custom-Forwarder'] = self.route_secret
        return headers

    def check_inactive_service(self):
        return

    def post(self, *args, **kwargs):
        self.check_inactive_service()
        return super().post(*args, **kwargs)

    def put(self, *args, **kwargs):
        self.check_inactive_service()
        return super().put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.check_inactive_service()
        return super().delete(*args, **kwargs)

    def get_users(self):
        users_data = self.get("/user")['data']
        return users_data


api_key = 'tester_yo-1be3e4a4-2046-4fbd-9190-76148ad68827-42f1af0d-4742-44dd-af79-8591d64d553e'
secret  = 'dev-notify-secret-key'

notifications_client = NotifyAdminAPIClient(
    api_key,
    base_url = 'http://localhost:6011'
)

#templates = notifications_client.get_all_templates()
#print(json.dumps(templates, indent=4, sort_keys=True))

users = notifications_client.get_users()
print(json.dumps(users, indent=4, sort_keys=True))
