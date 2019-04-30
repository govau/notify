from celery.exceptions import Retry

from notifications_utils.statsd_decorators import statsd

from app import notify_celery
from app.config import QueueNames
from app.notifications.notifications_ses_callback import (
    process_ses_results,
)


@notify_celery.task(bind=True, name="process-ses-result", max_retries=5, default_retry_delay=300)
@statsd(namespace="tasks")
def process_ses_results_task(self, response):
    try:
        ok, retry = process_ses_results(response)
        if retry:
            self.retry(queue=QueueNames.RETRY)
        return ok
    except Retry:
        raise
