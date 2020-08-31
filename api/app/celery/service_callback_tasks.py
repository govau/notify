import json

from flask import current_app
from datetime import datetime
from notifications_utils.statsd_decorators import statsd
from requests import (
    HTTPError,
    request,
    RequestException
)

from app import (
    notify_celery,
    encryption
)
from app.dao.callback_failures_dao import dao_create_callback_failure, dao_service_callbacks_are_failing
from app.dao.notifications_dao import dao_get_notification_history_by_id
from app.models import CallbackFailure
from app.config import QueueNames


@notify_celery.task(bind=True, name="send-delivery-status", max_retries=5, default_retry_delay=60)
@statsd(namespace="tasks")
def send_delivery_status_to_service(self, notification_id, encrypted_status_update):
    start_time = datetime.utcnow()
    status_update = encryption.decrypt(encrypted_status_update)

    try:
        data = {
            "id": str(notification_id),
            "reference": status_update['notification_client_reference'],
            "to": status_update['notification_to'],
            "status": status_update['notification_status'],
            "created_at": status_update['notification_created_at'],
            "completed_at": status_update['notification_updated_at'],
            "sent_at": status_update['notification_sent_at'],
            "notification_type": status_update['notification_type']
        }

        response = request(
            method="POST",
            url=status_update['service_callback_api_url'],
            data=json.dumps(data),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(status_update['service_callback_api_bearer_token'])
            },
            timeout=10
        )
        current_app.logger.info('send_delivery_status_to_service sending {} to {}, response {}'.format(
            notification_id,
            status_update['service_callback_api_url'],
            response.status_code
        ))
        response.raise_for_status()
    except RequestException as e:
        end_time = datetime.utcnow()
        current_app.logger.warning(
            "send_delivery_status_to_service request failed for notification_id: {} and url: {}. exc: {}".format(
                notification_id,
                status_update['service_callback_api_url'],
                e
            )
        )
        record_failed_status_callback.apply_async([], dict(
            notification_id=notification_id,
            service_id=status_update['service_id'],
            service_callback_url=status_update['service_callback_api_url'],
            notification_api_key_id=status_update['notification_api_key_id'],
            notification_api_key_type=status_update['notification_api_key_type'],
            callback_attempt_number=self.request.retries,
            callback_attempt_started=start_time,
            callback_attempt_ended=end_time,
            callback_failure_type=type(e).__name__,
            service_callback_type='send_delivery_status_to_service',
        ), queue=QueueNames.NOTIFY)

        if not isinstance(e, HTTPError) or e.response.status_code >= 500:
            service_id = status_update['service_id']
            if dao_service_callbacks_are_failing(service_id):
                current_app.logger.warning(
                    f"send_delivery_status_to_service retry cancelled for notification_id: {notification_id} due to failing service_id: {service_id}"
                )
                return

            try:
                self.retry(queue=QueueNames.RETRY)
            except self.MaxRetriesExceededError:
                current_app.logger.exception(
                    """Retry: send_delivery_status_to_service has retried the max num of times
                        for notification: {}""".format(notification_id)
                )


@notify_celery.task(bind=True, name="send-complaint", max_retries=5, default_retry_delay=300)
@statsd(namespace="tasks")
def send_complaint_to_service(self, complaint_data):
    complaint = encryption.decrypt(complaint_data)

    data = {
        "notification_id": complaint['notification_id'],
        "complaint_id": complaint['complaint_id'],
        "reference": complaint['reference'],
        "to": complaint['to'],
        "complaint_date": complaint['complaint_date']
    }

    _send_data_to_service_callback_api(
        self,
        data,
        complaint['service_callback_api_url'],
        complaint['service_callback_api_bearer_token'],
        'send_complaint_to_service'
    )


def _send_data_to_service_callback_api(self, data, service_callback_url, token, function_name):
    notification_id = (data["notification_id"] if "notification_id" in data else data["id"])
    try:
        response = request(
            method="POST",
            url=service_callback_url,
            data=json.dumps(data),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(token)
            },
            timeout=15
        )
        current_app.logger.info('{} sending {} to {}, response {}'.format(
            function_name,
            notification_id,
            service_callback_url,
            response.status_code
        ))
        response.raise_for_status()
    except RequestException as e:
        current_app.logger.warning(
            "{} request failed for notification_id: {} and url: {}. exc: {}".format(
                function_name,
                notification_id,
                service_callback_url,
                e
            )
        )
        if not isinstance(e, HTTPError) or e.response.status_code >= 500:
            try:
                self.retry(queue=QueueNames.RETRY)
            except self.MaxRetriesExceededError:
                current_app.logger.error(
                    "Retry: {} has retried the max num of times for callback url {} and notification_id: {}".format(
                        function_name,
                        service_callback_url,
                        notification_id
                    )
                )


def create_delivery_status_callback_data(notification, service_callback_api):
    from app import DATETIME_FORMAT, encryption
    data = {
        "notification_id": str(notification.id),
        "notification_client_reference": notification.client_reference,
        "notification_to": notification.to,
        "notification_status": notification.status,
        "notification_created_at": notification.created_at.strftime(DATETIME_FORMAT),
        "notification_updated_at":
            notification.updated_at.strftime(DATETIME_FORMAT) if notification.updated_at else None,
        "notification_sent_at": notification.sent_at.strftime(DATETIME_FORMAT) if notification.sent_at else None,
        "notification_type": notification.notification_type,
        "notification_api_key_id": str(notification.api_key_id) if notification.api_key_id else None,
        "notification_api_key_type": notification.key_type,
        "service_id": str(notification.service_id) if notification.service_id else None,
        "service_callback_api_url": notification.status_callback_url if notification.status_callback_url else service_callback_api.url,
        "service_callback_api_bearer_token": notification.status_callback_bearer_token if notification.status_callback_bearer_token else service_callback_api.bearer_token,
    }
    return encryption.encrypt(data)


def create_complaint_callback_data(complaint, notification, service_callback_api, recipient):
    from app import DATETIME_FORMAT, encryption
    data = {
        "complaint_id": str(complaint.id),
        "notification_id": str(notification.id),
        "reference": notification.client_reference,
        "to": recipient,
        "complaint_date": complaint.complaint_date.strftime(DATETIME_FORMAT),
        "service_callback_api_url": service_callback_api.url,
        "service_callback_api_bearer_token": service_callback_api.bearer_token,
    }
    return encryption.encrypt(data)


@notify_celery.task(name="record-failed-status-callback")
def record_failed_status_callback(
        *, notification_id, service_id, service_callback_url,
        notification_api_key_id, notification_api_key_type,
        callback_attempt_number, callback_attempt_started,
        callback_attempt_ended, callback_failure_type, service_callback_type):

    # A notification history entry will not exist if this notification was created with a test key.
    # To avoid a broken foreign key entry failure, we check to see if the history exists before
    # we attempt to create the failure record.
    notification = dao_get_notification_history_by_id(notification_id, _raise=False)
    callback_failure = CallbackFailure(
        notification_id=notification_id if notification else None,
        service_id=service_id,
        service_callback_url=service_callback_url,
        notification_api_key_id=notification_api_key_id,
        notification_api_key_type=notification_api_key_type,
        callback_attempt_number=callback_attempt_number,
        callback_attempt_started=callback_attempt_started,
        callback_attempt_ended=callback_attempt_ended,
        callback_failure_type=callback_failure_type,
        service_callback_type=service_callback_type,
    )
    dao_create_callback_failure(callback_failure)
