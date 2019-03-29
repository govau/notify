
from app.notify_client import NotifyAdminAPIClient

class SupportApiClient(NotifyAdminAPIClient):
    def __init__(self):
        super().__init__("a" * 73, "b")

    def post_support_ticket(self, data):
        return self.post('/support', data)
