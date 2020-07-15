import json
from datetime import datetime

import pytest
import requests_mock
from freezegun import freeze_time

from app import (DATETIME_FORMAT, encryption)
from app.celery.service_callback_tasks import send_delivery_status_to_service, send_complaint_to_service, create_delivery_status_callback_data, record_failed_status_callback
from app.dao.callback_failures_dao import dao_get_callback_failures_by_service_id
from tests.app.db import (
    create_complaint,
    create_notification,
    create_service_callback_api,
    create_service,
    create_template
)


@pytest.mark.parametrize("notification_type",
                         ["email", "letter", "sms"])
def test_send_delivery_status_to_service_post_https_request_to_service_with_encrypted_data(
        notify_db_session, notification_type, mocker):

    callback_api, template = _set_up_test_data(notification_type, "delivery_status")
    datestr = datetime(2017, 6, 20)

    notification = create_notification(template=template,
                                       created_at=datestr,
                                       updated_at=datestr,
                                       sent_at=datestr,
                                       status='sent'
                                       )
    encrypted_status_update = _set_up_data_for_status_update(callback_api, notification)
    record_failure_mock = mocker.patch('app.celery.service_callback_tasks.record_failed_status_callback.apply_async')
    with requests_mock.Mocker() as request_mock:
        request_mock.post(callback_api.url,
                          json={},
                          status_code=200)
        send_delivery_status_to_service(notification.id, encrypted_status_update=encrypted_status_update)

    mock_data = {
        "id": str(notification.id),
        "reference": notification.client_reference,
        "to": notification.to,
        "status": notification.status,
        "created_at": datestr.strftime(DATETIME_FORMAT),
        "completed_at": datestr.strftime(DATETIME_FORMAT),
        "sent_at": datestr.strftime(DATETIME_FORMAT),
        "notification_type": notification_type
    }

    record_failure_mock.assert_not_called()
    assert request_mock.call_count == 1
    assert request_mock.request_history[0].url == callback_api.url
    assert request_mock.request_history[0].method == 'POST'
    assert request_mock.request_history[0].text == json.dumps(mock_data)
    assert request_mock.request_history[0].headers["Content-type"] == "application/json"
    assert request_mock.request_history[0].headers["Authorization"] == "Bearer {}".format(callback_api.bearer_token)


def test_send_complaint_to_service_posts_https_request_to_service_with_encrypted_data(notify_db_session):
    with freeze_time('2001-01-01T12:00:00'):
        callback_api, template = _set_up_test_data('email', "complaint")

        notification = create_notification(template=template)
        complaint = create_complaint(service=template.service, notification=notification)
        complaint_data = _set_up_data_for_complaint(callback_api, complaint, notification)
        with requests_mock.Mocker() as request_mock:
            request_mock.post(callback_api.url,
                              json={},
                              status_code=200)
            send_complaint_to_service(complaint_data)

        mock_data = {
            "notification_id": str(notification.id),
            "complaint_id": str(complaint.id),
            "reference": notification.client_reference,
            "to": notification.to,
            "complaint_date": datetime.utcnow().strftime(
                DATETIME_FORMAT),
        }

        assert request_mock.call_count == 1
        assert request_mock.request_history[0].url == callback_api.url
        assert request_mock.request_history[0].method == 'POST'
        assert request_mock.request_history[0].text == json.dumps(mock_data)
        assert request_mock.request_history[0].headers["Content-type"] == "application/json"
        assert request_mock.request_history[0].headers["Authorization"] == "Bearer {}".format(callback_api.bearer_token)


@pytest.mark.parametrize("notification_type",
                         ["email", "letter", "sms"])
def test__send_data_to_service_callback_api_retries_if_request_returns_500_with_encrypted_data(
        notify_db_session, mocker, notification_type
):
    callback_api, template = _set_up_test_data(notification_type, "delivery_status")
    datestr = datetime(2017, 6, 20)
    notification = create_notification(template=template,
                                       created_at=datestr,
                                       updated_at=datestr,
                                       sent_at=datestr,
                                       status='sent'
                                       )
    encrypted_data = _set_up_data_for_status_update(callback_api, notification)
    record_failure_mock = mocker.patch('app.celery.service_callback_tasks.record_failed_status_callback.apply_async')
    mocked = mocker.patch('app.celery.service_callback_tasks.send_delivery_status_to_service.retry')
    with requests_mock.Mocker() as request_mock:
        request_mock.post(callback_api.url,
                          json={},
                          status_code=500)
        send_delivery_status_to_service(notification.id, encrypted_status_update=encrypted_data)

    record_failure_mock.assert_called()
    assert mocked.call_count == 1
    assert mocked.call_args[1]['queue'] == 'retry-tasks'


@pytest.mark.parametrize("notification_type",
                         ["email", "letter", "sms"])
def test__send_data_to_service_callback_api_does_not_retry_if_request_returns_404_with_encrypted_data(
        notify_db_session,
        mocker,
        notification_type
):
    callback_api, template = _set_up_test_data(notification_type, "delivery_status")
    datestr = datetime(2017, 6, 20)
    notification = create_notification(template=template,
                                       created_at=datestr,
                                       updated_at=datestr,
                                       sent_at=datestr,
                                       status='sent'
                                       )
    encrypted_data = _set_up_data_for_status_update(callback_api, notification)
    record_failure_mock = mocker.patch('app.celery.service_callback_tasks.record_failed_status_callback.apply_async')
    mocked = mocker.patch('app.celery.service_callback_tasks.send_delivery_status_to_service.retry')
    with requests_mock.Mocker() as request_mock:
        request_mock.post(callback_api.url,
                          json={},
                          status_code=404)
        send_delivery_status_to_service(notification.id, encrypted_status_update=encrypted_data)

    record_failure_mock.assert_called()
    assert mocked.call_count == 0


def test_send_delivery_status_to_service_succeeds_if_sent_at_is_none(
        notify_db_session,
        mocker
):
    callback_api, template = _set_up_test_data('email', "delivery_status")
    datestr = datetime(2017, 6, 20)

    notification = create_notification(template=template,
                                       created_at=datestr,
                                       updated_at=datestr,
                                       sent_at=None,
                                       status='technical-failure'
                                       )
    encrypted_data = _set_up_data_for_status_update(callback_api, notification)
    record_failure_mock = mocker.patch('app.celery.service_callback_tasks.record_failed_status_callback.apply_async')
    mocked = mocker.patch('app.celery.service_callback_tasks.send_delivery_status_to_service.retry')
    with requests_mock.Mocker() as request_mock:
        request_mock.post(callback_api.url,
                          json={},
                          status_code=404)
        send_delivery_status_to_service(notification.id, encrypted_status_update=encrypted_data)

    record_failure_mock.assert_called()
    assert mocked.call_count == 0


def test_send_delivery_status_records_failure_when_unsucessful(notify_db_session, mocker):
    callback_api, template = _set_up_test_data('sms', "delivery_status")
    datestr = datetime(2017, 6, 20)

    notification = create_notification(template=template,
                                       created_at=datestr,
                                       updated_at=datestr,
                                       sent_at=datestr,
                                       status='sent'
                                       )

    encrypted_status_update = _set_up_data_for_status_update(callback_api, notification)
    mocker.patch('app.celery.service_callback_tasks.send_delivery_status_to_service.retry')
    failure_mock = mocker.patch('app.celery.service_callback_tasks.record_failed_status_callback.apply_async')

    with requests_mock.Mocker() as request_mock:
        request_mock.post(callback_api.url, json={}, status_code=404)
        send_delivery_status_to_service(str(notification.id), encrypted_status_update=encrypted_status_update)

        assert request_mock.call_count == 1
        failure_mock.assert_called()
        ([], record_failure_args), kwargs = failure_mock.call_args
        failure_mock.assert_called_with([], dict(
            notification_id=str(notification.id),
            service_id=str(notification.service_id),
            service_callback_url=callback_api.url,
            notification_api_key_id=str(notification.api_key_id),
            notification_api_key_type=notification.key_type,
            callback_attempt_number=0,
            callback_attempt_started=record_failure_args['callback_attempt_started'],
            callback_attempt_ended=record_failure_args['callback_attempt_ended'],
            callback_failure_type='HTTPError',
            service_callback_type='send_delivery_status_to_service',
        ), queue='notify-internal-tasks')

    assert dao_get_callback_failures_by_service_id(notification.service_id).count() == 0
    record_failed_status_callback(**record_failure_args)
    assert dao_get_callback_failures_by_service_id(notification.service_id).count() == 1


def _set_up_test_data(notification_type, callback_type):
    service = create_service(restricted=True)
    template = create_template(service=service, template_type=notification_type, subject='Hello')
    callback_api = create_service_callback_api(service=service, url="https://some.service.gov.uk/",
                                               bearer_token="something_unique", callback_type=callback_type)
    return callback_api, template


def _set_up_data_for_status_update(callback_api, notification):
    return create_delivery_status_callback_data(notification, callback_api)


def _set_up_data_for_complaint(callback_api, complaint, notification):
    data = {
        "complaint_id": str(complaint.id),
        "notification_id": str(notification.id),
        "reference": notification.client_reference,
        "to": notification.to,
        "complaint_date": complaint.complaint_date.strftime(DATETIME_FORMAT),
        "service_callback_api_url": callback_api.url,
        "service_callback_api_bearer_token": callback_api.bearer_token,
    }
    obscured_status_update = encryption.encrypt(data)
    return obscured_status_update
