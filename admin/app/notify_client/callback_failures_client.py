from app.notify_client import NotifyAdminAPIClient, _attach_current_user


class CallbackFailuresClient(NotifyAdminAPIClient):
    # Fudge assert in the super __init__ so
    # we can set those variables later.
    def __init__(self):
        super().__init__("a" * 73, "b")

    def get_failing_callback_stats(self):
        return self.get("/service/failing-callback-stats")

    def get_failing_callbacks(self, page=1):
        params = {'page': page}
        return self.get("/service/failing-callbacks", params=params)

    def get_failing_callback_summary(self):
        return self.get("/service/failing-callback-summary")


callback_failures_client = CallbackFailuresClient()
