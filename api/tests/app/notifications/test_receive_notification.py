import base64
from datetime import datetime
from unittest.mock import call
import urllib.parse
from freezegun import freeze_time
import pytest

from app.notifications.receive_notifications import (
    create_inbound_sms_object,
    has_inbound_sms_permissions,
)

from app.models import InboundSms, EMAIL_TYPE, SMS_TYPE, INBOUND_SMS_TYPE
from tests.conftest import set_config_values
from tests.app.db import create_inbound_number, create_service, create_service_with_inbound_number
from tests.app.conftest import sample_service


def twilio_post(client, data, auth='username:password', signature='signature'):
    headers = [
        ('Content-Type', 'application/x-www-form-urlencoded'),
        ('X-Twilio-Signature', signature),
    ]

    if bool(auth):
        auth_value = base64.b64encode(auth.encode('utf-8')).decode('utf-8')
        headers.append(('Authorization', 'Basic ' + auth_value))

    return client.post(
        path='/notifications/sms/receive/twilio',
        data=data,
        headers=headers
    )


@pytest.mark.parametrize('permissions', [
    [SMS_TYPE],
    [INBOUND_SMS_TYPE],
])
def test_receive_notification_from_twilio_without_permissions_does_not_persist(
    client,
    mocker,
    notify_db_session,
    permissions
):
    mocker.patch('twilio.request_validator.RequestValidator.validate', return_value=True)

    service = create_service_with_inbound_number(inbound_number='+61412888888', service_permissions=permissions)
    mocker.patch("app.notifications.receive_notifications.dao_fetch_service_by_inbound_number",
                 return_value=service)
    mocked_send_inbound_sms = mocker.patch(
        "app.notifications.receive_notifications.tasks.send_inbound_sms_to_service.apply_async")
    mocker.patch("app.notifications.receive_notifications.has_inbound_sms_permissions", return_value=False)

    data = urllib.parse.urlencode({'MessageSid': '1', 'From': '+61412999999', 'To': '+61412888888', 'Body': 'this is a message'})

    response = twilio_post(client, data)

    assert response.status_code == 200
    assert response.get_data(as_text=True) == '<?xml version="1.0" encoding="UTF-8"?><Response />'
    assert InboundSms.query.count() == 0
    assert not mocked_send_inbound_sms.called


def test_receive_notification_without_permissions_does_not_create_inbound_even_with_inbound_number_set(
        client, mocker, notify_db, notify_db_session):
    mocker.patch('twilio.request_validator.RequestValidator.validate', return_value=True)

    service = sample_service(notify_db, notify_db_session, permissions=[SMS_TYPE])
    create_inbound_number('+61412345678', service_id=service.id, active=True)

    mocked_send_inbound_sms = mocker.patch(
        "app.notifications.receive_notifications.tasks.send_inbound_sms_to_service.apply_async")
    mocked_has_permissions = mocker.patch(
        "app.notifications.receive_notifications.has_inbound_sms_permissions", return_value=False)

    data = urllib.parse.urlencode({'MessageSid': '1', 'From': '+61412999999', 'To': '+61412345678', 'Body': 'this is a message'})

    response = twilio_post(client, data)

    assert response.status_code == 200
    assert len(InboundSms.query.all()) == 0
    assert mocked_has_permissions.called
    mocked_send_inbound_sms.assert_not_called()


@pytest.mark.parametrize('permissions,expected_response', [
    ([SMS_TYPE, INBOUND_SMS_TYPE], True),
    ([INBOUND_SMS_TYPE], False),
    ([SMS_TYPE], False),
])
def test_check_permissions_for_inbound_sms(notify_db, notify_db_session, permissions, expected_response):
    service = create_service(service_permissions=permissions)
    assert has_inbound_sms_permissions(service.permissions) is expected_response


@freeze_time('2017-01-01T16:00:00')
def test_create_inbound_sms_object(sample_service_full_permissions):
    inbound_sms = create_inbound_sms_object(
        sample_service_full_permissions,
        'hello there 📩',
        '+61412345678',
        'bar',
        'twilio',
    )

    assert inbound_sms.service_id == sample_service_full_permissions.id
    assert inbound_sms.notify_number == sample_service_full_permissions.get_inbound_number()
    assert inbound_sms.user_number == '+61412345678'
    assert inbound_sms.provider_date == datetime(2017, 1, 1, 16, 00, 00)
    assert inbound_sms.provider_reference == 'bar'
    assert inbound_sms._content != 'hello there 📩'
    assert inbound_sms.content == 'hello there 📩'
    assert inbound_sms.provider == 'twilio'


@pytest.mark.parametrize('notify_number', ['+61412000000', '+61412111111'], ids=['two_matching_services', 'no_matching_services'])
def test_receive_notification_error_if_not_single_matching_service(client, mocker, notify_db_session, notify_number):
    mocker.patch('twilio.request_validator.RequestValidator.validate', return_value=True)

    create_service_with_inbound_number(
        inbound_number='+61412222222',
        service_name='a',
        service_permissions=[EMAIL_TYPE, SMS_TYPE, INBOUND_SMS_TYPE]
    )
    create_service_with_inbound_number(
        inbound_number='+6141333333',
        service_name='b',
        service_permissions=[EMAIL_TYPE, SMS_TYPE, INBOUND_SMS_TYPE]
    )

    data = urllib.parse.urlencode({'MessageSid': '1', 'From': notify_number, 'To': '+61412888888', 'Body': 'hello'})
    response = twilio_post(client, data)

    assert response.status_code == 200
    assert response.get_data(as_text=True) == '<?xml version="1.0" encoding="UTF-8"?><Response />'
    assert InboundSms.query.count() == 0


def test_receive_notification_returns_received_to_twilio(notify_db_session, client, mocker):
    mocker.patch('twilio.request_validator.RequestValidator.validate', return_value=True)
    mocked = mocker.patch("app.notifications.receive_notifications.tasks.send_inbound_sms_to_service.apply_async")
    mock = mocker.patch('app.notifications.receive_notifications.statsd_client.incr')

    service = create_service_with_inbound_number(
        service_name='b', inbound_number='+61412888888', service_permissions=[EMAIL_TYPE, SMS_TYPE, INBOUND_SMS_TYPE])

    data = urllib.parse.urlencode({'MessageSid': '1', 'From': '+61412999999', 'To': '+61412888888', 'Body': 'this is a message'})

    response = twilio_post(client, data)

    assert response.status_code == 200
    assert response.get_data(as_text=True) == '<?xml version="1.0" encoding="UTF-8"?><Response />'
    mock.assert_has_calls([call('inbound.twilio.successful')])
    inbound_sms_id = InboundSms.query.all()[0].id
    mocked.assert_called_once_with([str(inbound_sms_id), str(service.id)], queue="notify-internal-tasks")


@freeze_time('2017-01-01T01:00:00')
def test_receive_notification_from_twilio_persists_message(notify_db_session, client, mocker):
    mocker.patch('twilio.request_validator.RequestValidator.validate', return_value=True)
    mocked = mocker.patch("app.notifications.receive_notifications.tasks.send_inbound_sms_to_service.apply_async")
    mocker.patch('app.notifications.receive_notifications.statsd_client.incr')

    service = create_service_with_inbound_number(
        inbound_number='+61412345678',
        service_name='b',
        service_permissions=[EMAIL_TYPE, SMS_TYPE, INBOUND_SMS_TYPE])

    data = urllib.parse.urlencode({'MessageSid': '1', 'From': '+61487654321', 'To': '+61412345678', 'Body': 'this is a message'})

    response = twilio_post(client, data)

    assert response.status_code == 200
    assert response.get_data(as_text=True) == '<?xml version="1.0" encoding="UTF-8"?><Response />'
    persisted = InboundSms.query.first()
    assert persisted is not None
    assert persisted.notify_number == '+61412345678'
    assert persisted.user_number == '+61487654321'
    assert persisted.service == service
    assert persisted.content == 'this is a message'
    assert persisted.provider == 'twilio'
    assert persisted.provider_date == datetime(2017, 1, 1, 1, 0, 0, 0)
    mocked.assert_called_once_with([str(persisted.id), str(service.id)], queue="notify-internal-tasks")


def test_receive_notification_from_twilio_persists_message_with_normalized_phone(notify_db_session, client, mocker):
    mocker.patch('twilio.request_validator.RequestValidator.validate', return_value=True)
    mocker.patch("app.notifications.receive_notifications.tasks.send_inbound_sms_to_service.apply_async")
    mocker.patch('app.notifications.receive_notifications.statsd_client.incr')

    create_service_with_inbound_number(
        inbound_number='+61412345678', service_name='b', service_permissions=[EMAIL_TYPE, SMS_TYPE, INBOUND_SMS_TYPE])

    data = urllib.parse.urlencode({'MessageSid': '1', 'From': '+61412999999', 'To': '+61412345678', 'Body': 'this is a message'})

    response = twilio_post(client, data)

    assert response.status_code == 200
    assert response.get_data(as_text=True) == '<?xml version="1.0" encoding="UTF-8"?><Response />'
    persisted = InboundSms.query.first()
    assert persisted is not None
    assert persisted.user_number == '+61412999999'


def test_returns_ok_to_twilio_if_mismatched_sms_sender(notify_db_session, client, mocker):
    mocker.patch('twilio.request_validator.RequestValidator.validate', return_value=True)
    mocked = mocker.patch("app.notifications.receive_notifications.tasks.send_inbound_sms_to_service.apply_async")
    mock = mocker.patch('app.notifications.receive_notifications.statsd_client.incr')

    create_service_with_inbound_number(
        inbound_number='+61412345678', service_name='b', service_permissions=[EMAIL_TYPE, SMS_TYPE, INBOUND_SMS_TYPE])

    data = urllib.parse.urlencode({'MessageSid': '1', 'From': '+61412999999', 'To': '+61412000000', 'Body': 'this is a message'})

    response = twilio_post(client, data)

    assert response.status_code == 200
    assert response.get_data(as_text=True) == '<?xml version="1.0" encoding="UTF-8"?><Response />'
    assert not InboundSms.query.all()
    mock.assert_has_calls([call('inbound.twilio.failed')])
    mocked.call_count == 0


@pytest.mark.parametrize("auth, usernames, passwords, status_code", [
    ["username:password", ["username"], ["password"], 200],
    ["username2:password", ["username", "username2"], ["password"], 200],
    ["username:password2", ["username"], ["password", "password2"], 200],
    ["", ["username"], ["password"], 401],
    ["", [], [], 401],
    ["username", ["username"], ["password"], 401],
    ["username:", ["username"], ["password"], 403],
    [":password", ["username"], ["password"], 403],
    ["wrong:password", ["username"], ["password"], 403],
    ["username:wrong", ["username"], ["password"], 403],
    ["username:password", [], [], 403],
])
def test_twilio_inbound_sms_auth(notify_db_session, notify_api, client, mocker, auth, usernames, passwords, status_code):
    mocker.patch('twilio.request_validator.RequestValidator.validate', return_value=True)
    mocker.patch("app.notifications.receive_notifications.tasks.send_inbound_sms_to_service.apply_async")

    create_service_with_inbound_number(
        service_name='b', inbound_number='+61412345678', service_permissions=[EMAIL_TYPE, SMS_TYPE, INBOUND_SMS_TYPE]
    )

    data = urllib.parse.urlencode({'MessageSid': '1', 'From': '+61412999999', 'To': '+61412345678', 'Body': 'this is a message'})

    with set_config_values(notify_api, {
        'TWILIO_INBOUND_SMS_USERNAMES': usernames,
        'TWILIO_INBOUND_SMS_PASSWORDS': passwords,
    }):
        response = twilio_post(client, data, auth=auth)
        assert response.status_code == status_code


def test_create_inbound_sms_object_works_with_alphanumeric_sender(sample_service_full_permissions):
    inbound_sms = create_inbound_sms_object(
        service=sample_service_full_permissions,
        content='hello',
        from_number='ALPHANUM3R1C',
        provider_ref='foo',
        provider_name="twilio"
    )

    assert inbound_sms.user_number == 'ALPHANUM3R1C'
