from flask import current_app
from app.config import QueueNames
from app.celery.service_callback_tasks import (
    send_delivery_status_to_service,
    create_delivery_status_callback_data,
)
from app.dao.service_callback_api_dao import get_service_delivery_status_callback_api_for_service
from app.dao.callback_failures_dao import dao_service_callbacks_are_failing


def check_for_callback_and_send_delivery_status_to_service(notification):
    service_callback_api = get_service_delivery_status_callback_api_for_service(service_id=notification.service_id)

    # If a status callback was provided on the notification or if the service
    # has a service_callback_api record, then queue the callback task.
    if (notification.status_callback_url and notification.status_callback_bearer_token) or service_callback_api:
        if dao_service_callbacks_are_failing(notification.service_id):
            current_app.logger.warning(
                f"send_delivery_status_to_service not called for notification_id: {notification.id} due to failing service_id: {notification.service_id}"
            )
            return

        encrypted_notification = create_delivery_status_callback_data(notification, service_callback_api)
        send_delivery_status_to_service.apply_async(
            [str(notification.id), encrypted_notification],
            queue=QueueNames.CALLBACKS,
        )
