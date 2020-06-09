import uuid
from datetime import datetime

from flask import current_app

from notifications_utils.clients import redis
from notifications_utils.recipients import (
    get_international_phone_info,
    validate_and_format_phone_number_and_require_local,
    validate_and_format_phone_number_and_allow_international,
    format_email_address
)

from app import redis_store
from app.celery import provider_tasks
from app.config import QueueNames

from app.models import (
    EMAIL_TYPE,
    KEY_TYPE_TEST,
    SMS_TYPE,
    NOTIFICATION_CREATED,
    Notification,
    ScheduledNotification
)
from app.dao.notifications_dao import (
    dao_create_notification,
    dao_delete_notifications_and_history_by_id,
    dao_created_scheduled_notification
)

from app.v2.errors import BadRequestError
from app.utils import (
    cache_key_for_service_template_counter,
    cache_key_for_service_template_usage_per_day,
    convert_aet_to_utc,
    convert_utc_to_aet,
    get_template_instance,
)


def create_content_for_notification(template, personalisation):
    template_object = get_template_instance(template.__dict__, personalisation)
    check_placeholders(template_object)

    return template_object


def check_placeholders(template_object):
    if template_object.missing_data:
        message = 'Missing personalisation: {}'.format(", ".join(template_object.missing_data))
        raise BadRequestError(fields=[{'template': message}], message=message)


def prepare_notification(
    *,
    template_id,
    template_version,
    recipient,
    service,
    personalisation,
    notification_type,
    api_key_id,
    key_type,
    created_at=None,
    job_id=None,
    job_row_number=None,
    reference=None,
    client_reference=None,
    notification_id=None,
    simulated=False,
    created_by_id=None,
    status=NOTIFICATION_CREATED,
    reply_to_text=None,
    status_callback_url=None,
    status_callback_bearer_token=None,
):
    notification_created_at = created_at or datetime.utcnow()
    if not notification_id:
        notification_id = uuid.uuid4()
    notification = Notification(
        id=notification_id,
        template_id=template_id,
        template_version=template_version,
        to=recipient,
        service_id=service.id,
        service=service,
        personalisation=personalisation,
        notification_type=notification_type,
        api_key_id=api_key_id,
        key_type=key_type,
        created_at=notification_created_at,
        job_id=job_id,
        job_row_number=job_row_number,
        client_reference=client_reference,
        reference=reference,
        created_by_id=created_by_id,
        status=status,
        reply_to_text=reply_to_text,
        status_callback_url=status_callback_url,
        status_callback_bearer_token=status_callback_bearer_token,
    )

    if notification_type == SMS_TYPE:
        formatted_recipient = validate_and_format_phone_number_and_allow_international(recipient)
        recipient_info = get_international_phone_info(formatted_recipient)
        notification.normalised_to = formatted_recipient
        notification.international = recipient_info.international
        notification.phone_prefix = recipient_info.country_prefix
        notification.rate_multiplier = recipient_info.billable_units

        # We can't use a sender name/ID if the text is sending to an
        # international number. At the time of writing, this is because Telstra
        # won't send to an international number unless sending from the number
        # associated with the subscription. Additionally, Twilio can send from a
        # sender name/ID, however, it requires configuration and it depends on
        # the countries in play.
        if notification.international:
            notification.reply_to_text = None

    elif notification_type == EMAIL_TYPE:
        notification.normalised_to = format_email_address(notification.to)

    return notification

def store_notification(notification):
    dao_create_notification(notification)
    notification_id = notification.id
    notification_type = notification.notification_type
    created_at = notification.created_at
    current_app.logger.info(f"{notification_type} {notification_id} created at {created_at}")

    if notification.key_type == KEY_TYPE_TEST:
        return notification

    service_id = notification.service_id
    template_id = notification.template_id
    if redis_store.get(redis.daily_limit_cache_key(service_id)):
        redis_store.incr(redis.daily_limit_cache_key(service_id))
    if redis_store.get_all_from_hash(cache_key_for_service_template_counter(service_id)):
        redis_store.increment_hash_value(cache_key_for_service_template_counter(service_id), template_id)
        increment_template_usage_cache(service_id, template_id, notification.created_at)

    return notification

def store_notifications(notifications, template):
    def not_test_notification(notification):
        return notification.key_type != KEY_TYPE_TEST

    dao_create_notifications(notifications)

    non_test_notifications = filter(not_test_notification, notifications)
    num_real_notifications = len(non_test_notifications)

    service = template.service
    if redis_store.get(redis.daily_limit_cache_key(service.id)):
        redis_store.incr(redis.daily_limit_cache_key(service.id), incr_by=num_real_notifications)
    if redis_store.get_all_from_hash(cache_key_for_service_template_counter(service.id)):
        redis_store.increment_hash_value(cache_key_for_service_template_counter(service.id), template_id, incr_by=num_real_notifications)
        increment_template_usage_cache(service.id, template_id, notification.created_at, incr_by=num_real_notifications)

    return notifications



def persist_notification(*, simulated=False, **kwargs):
    notification = prepare_notification(**kwargs)
    if not simulated:
        store_notification(notification)

    return notification


def increment_template_usage_cache(service_id, template_id, created_at, incr_by=1):
    key = cache_key_for_service_template_usage_per_day(service_id, convert_utc_to_aet(created_at))
    redis_store.increment_hash_value(key, template_id, incr_by=incr_by)
    # set key to expire in eight days - we don't know if we've just created the key or not, so must assume that we
    # have and reset the expiry. Eight days is longer than any notification is in the notifications table, so we'll
    # always capture the full week's numbers
    redis_store.expire(key, current_app.config['EXPIRE_CACHE_EIGHT_DAYS'])


def send_notification_to_queue(notification, research_mode, queue=None):
    if research_mode or notification.key_type == KEY_TYPE_TEST:
        queue = QueueNames.RESEARCH_MODE

    if notification.notification_type == SMS_TYPE:
        if not queue:
            queue = QueueNames.SEND_SMS
        deliver_task = provider_tasks.deliver_sms
    if notification.notification_type == EMAIL_TYPE:
        if not queue:
            queue = QueueNames.SEND_EMAIL
        deliver_task = provider_tasks.deliver_email

    try:
        deliver_task.apply_async([str(notification.id)], queue=queue)
    except Exception:
        dao_delete_notifications_and_history_by_id(notification.id)
        raise

    current_app.logger.debug(
        "{} {} sent to the {} queue for delivery".format(notification.notification_type,
                                                         notification.id,
                                                         queue))


def simulated_recipient(to_address, notification_type):
    if notification_type == SMS_TYPE:
        formatted_simulated_numbers = [
            validate_and_format_phone_number_and_require_local(number) for number in current_app.config['SIMULATED_SMS_NUMBERS']
        ]
        return to_address in formatted_simulated_numbers
    else:
        return to_address in current_app.config['SIMULATED_EMAIL_ADDRESSES']


def persist_scheduled_notification(notification_id, scheduled_for):
    scheduled_datetime = convert_aet_to_utc(datetime.strptime(scheduled_for, "%Y-%m-%d %H:%M"))
    scheduled_notification = ScheduledNotification.for_notification(notification_id, scheduled_datetime)
    dao_created_scheduled_notification(scheduled_notification)
