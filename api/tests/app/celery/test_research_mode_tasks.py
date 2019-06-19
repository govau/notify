import uuid
from unittest.mock import ANY

from flask import current_app, json
from freezegun import freeze_time
import pytest
import requests_mock

from app.config import QueueNames
from app.celery.research_mode_tasks import (
    send_sms_response,
    send_email_response,
    telstra_callback,
    twilio_callback,
    ses_notification_callback,
    create_fake_letter_response_file,
)
from tests.conftest import set_config_values


def test_make_telstra_callback(notify_api, rmock):
    endpoint = "http://localhost:6011/notifications/sms/telstra/1234"
    rmock.request(
        "POST",
        endpoint,
        json={"status": "success"},
        status_code=200)
    send_sms_response("telstra", "1234", "0409000001")

    assert rmock.called
    assert rmock.request_history[0].url == endpoint
    assert json.loads(rmock.request_history[0].text)['to'] == '0409000001'


@pytest.mark.parametrize("phone_number",
                         ["0409000001", "0409000002", "0409000003",
                          "0412345678"])
def test_make_twilio_callback(notify_api, rmock, phone_number):
    endpoint = "http://localhost:6011/notifications/sms/twilio/1234"
    rmock.request(
        "POST",
        endpoint,
        json="some data",
        status_code=200)
    send_sms_response("twilio", "1234", phone_number)

    assert rmock.called
    assert rmock.request_history[0].url == endpoint
    assert 'To={}'.format(phone_number) in rmock.request_history[0].text


def test_make_ses_callback(notify_api, mocker):
    mock_task = mocker.patch('app.celery.research_mode_tasks.process_ses_results_task')
    some_ref = str(uuid.uuid4())

    send_email_response(reference=some_ref, to="test@test.com")

    mock_task.apply_async.assert_called_once_with(ANY, queue=QueueNames.RESEARCH_MODE)
    assert mock_task.apply_async.call_args[0][0][0] == ses_notification_callback(some_ref)


@pytest.mark.parametrize("phone_number", ["0409000001", "+61409000001", "409000001", "+61 409000001",
                                          "+61412345678"])
def test_delivered_telstra_callback(phone_number):
    data = json.loads(telstra_callback("1234", phone_number))
    assert data['to'] == phone_number
    assert data['deliveryStatus'] == "DELIVRD"


@pytest.mark.parametrize("phone_number", ["0409000002", "+61409000002", "409000002", "+61 409000002"])
def test_perm_failure_telstra_callback(phone_number):
    data = json.loads(telstra_callback("1234", phone_number))
    assert data['to'] == phone_number
    assert data['deliveryStatus'] == "UNDVBL"


@pytest.mark.parametrize("phone_number", ["0409000003", "+61409000003", "409000003", "+61 409000003"])
def test_temp_failure_telstra_callback(phone_number):
    data = json.loads(telstra_callback("1234", phone_number))
    assert data['to'] == phone_number
    assert data['deliveryStatus'] == "REJECTED"


@pytest.mark.parametrize("phone_number", ["0409000001", "+61409000001", "409000001", "+61 409000001",
                                          "+614123456"])
def test_delivered_twilio_callback(phone_number):
    assert twilio_callback('1234', phone_number) == {
        "AccountSid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "ApiVersion": "2010-04-01",
        "From": "+14155552345",
        "MessageSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "MessageStatus": "delivered",
        "SmsSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "SmsStatus": "delivered",
        "To": phone_number,
    }


@pytest.mark.parametrize("phone_number", ["0409000002", "+61409000002", "409000002", "+61 409000002"])
def test_failure_twilio_callback(phone_number):
    assert twilio_callback('1234', phone_number) == {
        "AccountSid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "ApiVersion": "2010-04-01",
        "From": "+14155552345",
        "MessageSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "MessageStatus": "undelivered",
        "SmsSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "SmsStatus": "undelivered",
        "To": phone_number,
    }


@freeze_time("2018-01-25 14:00:00")
def test_create_fake_letter_response_file_uploads_response_file_s3(
        notify_api, mocker):
    mock_s3upload = mocker.patch('app.celery.research_mode_tasks.s3upload')
    filename = 'NOTIFY-20180125140000-RSP.TXT'

    with requests_mock.Mocker() as request_mock:
        request_mock.post(
            'http://localhost:6011/notifications/letter/dvla/example-ref',
            content=b'{}',
            status_code=200
        )

        create_fake_letter_response_file('example-ref')

        mock_s3upload.assert_called_once_with(
            filedata='example-ref|Sent|0|Sorted',
            region=current_app.config['AWS_REGION'],
            bucket_name=current_app.config['DVLA_RESPONSE_BUCKET_NAME'],
            file_location=filename
        )


@freeze_time("2018-01-25 14:00:00")
def test_create_fake_letter_response_file_calls_dvla_callback_on_development(
        notify_api, mocker):
    mocker.patch('app.celery.research_mode_tasks.s3upload')
    filename = 'NOTIFY-20180125140000-RSP.TXT'

    with set_config_values(notify_api, {
        'NOTIFY_ENVIRONMENT': 'development'
    }):
        with requests_mock.Mocker() as request_mock:
            request_mock.post(
                'http://localhost:6011/notifications/letter/dvla/example-ref',
                content=b'{}',
                status_code=200
            )

            create_fake_letter_response_file('example-ref')

            assert request_mock.last_request.json() == {
                "Type": "Notification",
                "MessageId": "some-message-id",
                "Message": '{"Records":[{"s3":{"object":{"key":"' + filename + '"}}}]}'
            }


@freeze_time("2018-01-25 14:00:00")
def test_create_fake_letter_response_file_does_not_call_dvla_callback_on_preview(
        notify_api, mocker):
    mocker.patch('app.celery.research_mode_tasks.s3upload')

    with set_config_values(notify_api, {
        'NOTIFY_ENVIRONMENT': 'preview'
    }):
        with requests_mock.Mocker() as request_mock:
            create_fake_letter_response_file('example-ref')

            assert request_mock.last_request is None
