import uuid
import urllib.parse
from datetime import datetime
from requests.auth import _basic_auth_str
import pytest
from flask import json
from freezegun import freeze_time

import app.celery.tasks
from app.clients import ClientException
from app.dao.notifications_dao import (
    get_notification_by_id
)
from tests.app.conftest import sample_notification as create_sample_notification


def fetch_sap_oauth2_token(client, oauth2_client):
    data = {'grant_type': 'client_credentials'}
    headers = [
        ('Authorization', _basic_auth_str(oauth2_client.client_id, oauth2_client.client_secret)),
        ('Content-Type', 'application/x-www-form-urlencoded')
    ]
    response = client.post(
        '/sap/oauth2/token',
        data=urllib.parse.urlencode(data),
        headers=headers,
    )
    return json.loads(response.get_data(as_text=True))['access_token']


def sap_post(client, oauth2_client, notification_id, data):
    access_token = fetch_sap_oauth2_token(client, oauth2_client)

    return client.post(
        path='/notifications/sms/sap/{}'.format(notification_id),
        data=json.dumps(data),
        headers=[
            ('Authorization', f'Bearer {access_token}'),
            ('Content-Type', 'application/json'),
            ('X-Forwarded-For', '203.0.113.195, 70.41.3.18, 150.172.238.178')  # fake IPs
        ])


def dvla_post(client, data):
    return client.post(
        path='/notifications/letter/dvla/example-ref',
        data=data,
        headers=[('Content-Type', 'application/json')]
    )


def test_dvla_callback_returns_400_with_invalid_request(client):
    data = json.dumps({"foo": "bar"})
    response = dvla_post(client, data)
    assert response.status_code == 400


def test_dvla_callback_autoconfirms_subscription(client, mocker):
    autoconfirm_mock = mocker.patch('app.notifications.notifications_letter_callback.autoconfirm_subscription')

    data = _sns_confirmation_callback()
    response = dvla_post(client, data)
    assert response.status_code == 200
    assert autoconfirm_mock.called


def test_dvla_callback_autoconfirm_does_not_call_update_letter_notifications_task(client, mocker):
    autoconfirm_mock = mocker.patch('app.notifications.notifications_letter_callback.autoconfirm_subscription')
    update_task = \
        mocker.patch('app.notifications.notifications_letter_callback.update_letter_notifications_statuses.apply_async')

    data = _sns_confirmation_callback()
    response = dvla_post(client, data)

    assert response.status_code == 200
    assert autoconfirm_mock.called
    assert not update_task.called


def test_dvla_callback_calls_does_not_update_letter_notifications_task_with_invalid_file_type(client, mocker):
    update_task = \
        mocker.patch('app.notifications.notifications_letter_callback.update_letter_notifications_statuses.apply_async')

    data = _sample_sns_s3_callback("bar.txt")
    response = dvla_post(client, data)

    assert response.status_code == 200
    assert not update_task.called


def test_dvla_rs_txt_file_callback_calls_update_letter_notifications_task(client, mocker):
    update_task = \
        mocker.patch('app.notifications.notifications_letter_callback.update_letter_notifications_statuses.apply_async')
    data = _sample_sns_s3_callback('Notify-20170411153023-rs.txt')
    response = dvla_post(client, data)

    assert response.status_code == 200
    assert update_task.called
    update_task.assert_called_with(['Notify-20170411153023-rs.txt'], queue='notify-internal-tasks')


def test_dvla_rsp_txt_file_callback_calls_update_letter_notifications_task(client, mocker):
    update_task = \
        mocker.patch('app.notifications.notifications_letter_callback.update_letter_notifications_statuses.apply_async')
    data = _sample_sns_s3_callback('NOTIFY-20170823160812-RSP.TXT')
    response = dvla_post(client, data)

    assert response.status_code == 200
    assert update_task.called
    update_task.assert_called_with(['NOTIFY-20170823160812-RSP.TXT'], queue='notify-internal-tasks')


def test_dvla_ack_calls_does_not_call_letter_notifications_task(client, mocker):
    update_task = \
        mocker.patch('app.notifications.notifications_letter_callback.update_letter_notifications_statuses.apply_async')
    data = _sample_sns_s3_callback('bar.ack.txt')
    response = dvla_post(client, data)

    assert response.status_code == 200
    update_task.assert_not_called()


def test_sap_callback_should_not_need_auth(client, sample_sap_oauth2_client, notify_db, notify_db_session, mocker):
    mocker.patch('app.statsd_client.incr')

    notification = create_sample_notification(
        notify_db, notify_db_session, status='sending', sent_at=datetime.utcnow()
    )

    data = {
        "messageId": "1234",
        "status": "SENT",
        "recipient": "+61412345678",
        "message": "message"
    }

    response = sap_post(client, sample_sap_oauth2_client, notification.id, data)

    assert response.status_code == 200


def test_sap_callback_should_return_400_if_no_status(client, sample_sap_oauth2_client, notify_db, notify_db_session, mocker):
    mocker.patch('app.statsd_client.incr')

    notification = create_sample_notification(
        notify_db, notify_db_session, status='sending', sent_at=datetime.utcnow()
    )

    data = {
        "messageId": "1234",
        "recipient": "+61412345678",
        "message": "message"
    }

    response = sap_post(client, sample_sap_oauth2_client, notification.id, data)
    json_resp = json.loads(response.get_data(as_text=True))

    assert response.status_code == 400
    assert json_resp['result'] == 'error'
    assert json_resp['message'] == ['SAP callback failed: status missing']


def test_sap_callback_should_set_status_technical_failure_if_status_unknown(client, sample_sap_oauth2_client, notify_db, notify_db_session, mocker):
    mocker.patch('app.statsd_client.incr')

    notification = create_sample_notification(
        notify_db, notify_db_session, status='sending', sent_at=datetime.utcnow()
    )

    data = {
        "messageId": "1234",
        "status": "UNKNOWN",
        "recipient": "+61412345678",
        "message": "message"
    }

    with pytest.raises(ClientException) as e:
        sap_post(client, sample_sap_oauth2_client, notification.id, data)

    assert get_notification_by_id(notification.id).status == 'technical-failure'
    assert 'SAP callback failed: status UNKNOWN not found.' in str(e.value)


def test_sap_callback_returns_200_when_notification_id_is_not_a_valid_uuid(client, sample_sap_oauth2_client, mocker):
    mocker.patch('app.statsd_client.incr')

    data = {
        "messageId": "1234",
        "status": "SENT",
        "recipient": "+61412345678",
        "message": "message"
    }

    response = sap_post(client, sample_sap_oauth2_client, "1234", data)
    json_resp = json.loads(response.get_data(as_text=True))

    assert response.status_code == 400
    assert json_resp['result'] == 'error'
    assert json_resp['message'] == 'SAP callback with invalid reference 1234'


def test_sap_callback_returns_200_if_notification_not_found(client, sample_sap_oauth2_client, notify_db, notify_db_session, mocker):
    mocker.patch('app.statsd_client.incr')

    missing_notification_id = uuid.uuid4()

    data = {
        "messageId": "1234",
        "status": "SENT",
        "recipient": "+61412345678",
        "message": "message"
    }

    response = sap_post(client, sample_sap_oauth2_client, missing_notification_id, data)
    json_resp = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert json_resp['result'] == 'success'


def test_sap_callback_should_update_notification_status(notify_db, notify_db_session, client, sample_sap_oauth2_client, sample_email_template, mocker):
    mocker.patch('app.statsd_client.incr')
    send_mock = mocker.patch(
        'app.celery.service_callback_tasks.send_delivery_status_to_service.apply_async'
    )

    notification = create_sample_notification(
        notify_db,
        notify_db_session,
        template=sample_email_template,
        reference='ref',
        status='sending',
        sent_at=datetime.utcnow())

    original = get_notification_by_id(notification.id)

    assert original.status == 'sending'

    data = {
        "messageId": "1234",
        "status": "DELIVERED",
        "recipient": "+61412345678",
        "message": "message"
    }

    response = sap_post(client, sample_sap_oauth2_client, notification.id, data)
    json_resp = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert json_resp['result'] == 'success'
    assert json_resp['message'] == 'SAP callback succeeded. reference {} updated'.format(
        notification.id
    )

    updated = get_notification_by_id(notification.id)

    assert updated.status == 'delivered'
    assert get_notification_by_id(notification.id).status == 'delivered'
    assert send_mock.called_once_with([notification.id], queue="notify-internal-tasks")


def test_sap_callback_should_update_notification_status_failed(notify_db, notify_db_session, client, sample_sap_oauth2_client, sample_template, mocker):
    mocker.patch('app.statsd_client.incr')
    mocker.patch(
        'app.celery.service_callback_tasks.send_delivery_status_to_service.apply_async'
    )

    notification = create_sample_notification(
        notify_db,
        notify_db_session,
        template=sample_template,
        reference='ref',
        status='sending',
        sent_at=datetime.utcnow())

    original = get_notification_by_id(notification.id)

    assert original.status == 'sending'

    data = {
        "messageId": "1234",
        "status": "ERROR",
        "recipient": "+61412345678",
        "message": "message"
    }

    response = sap_post(client, sample_sap_oauth2_client, notification.id, data)
    json_resp = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert json_resp['result'] == 'success'
    assert json_resp['message'] == 'SAP callback succeeded. reference {} updated'.format(
        notification.id
    )
    assert get_notification_by_id(notification.id).status == 'permanent-failure'


def test_sap_callback_should_record_statsd(client, sample_sap_oauth2_client, notify_db, notify_db_session, mocker):
    with freeze_time('2001-01-01T12:00:00'):
        mocker.patch('app.statsd_client.incr')
        mocker.patch('app.statsd_client.timing_with_dates')
        mocker.patch(
            'app.celery.service_callback_tasks.send_delivery_status_to_service.apply_async'
        )

        notification = create_sample_notification(
            notify_db, notify_db_session, status='sending', sent_at=datetime.utcnow()
        )

        data = {
            "messageId": "1234",
            "status": "DELIVERED",
            "recipient": "+61412345678",
            "message": "message"
        }

        sap_post(client, sample_sap_oauth2_client, notification.id, data)

        app.statsd_client.timing_with_dates.assert_any_call(
            "callback.sap.elapsed-time", datetime.utcnow(), notification.sent_at
        )
        app.statsd_client.incr.assert_any_call("callback.sap.delivered")


def _sample_sns_s3_callback(filename):
    message_contents = '''{"Records":[{"eventVersion":"2.0","eventSource":"aws:s3","awsRegion":"eu-west-1","eventTime":"2017-05-16T11:38:41.073Z","eventName":"ObjectCreated:Put","userIdentity":{"principalId":"some-p-id"},"requestParameters":{"sourceIPAddress":"8.8.8.8"},"responseElements":{"x-amz-request-id":"some-r-id","x-amz-id-2":"some-x-am-id"},"s3":{"s3SchemaVersion":"1.0","configurationId":"some-c-id","bucket":{"name":"some-bucket","ownerIdentity":{"principalId":"some-p-id"},"arn":"some-bucket-arn"},
            "object":{"key":"%s"}}}]}''' % (filename)  # noqa
    return json.dumps({
        "SigningCertURL": "foo.pem",
        "UnsubscribeURL": "bar",
        "Signature": "some-signature",
        "Type": "Notification",
        "Timestamp": "2016-05-03T08:35:12.884Z",
        "SignatureVersion": "1",
        "MessageId": "6adbfe0a-d610-509a-9c47-af894e90d32d",
        "Subject": "Amazon S3 Notification",
        "TopicArn": "sample-topic-arn",
        "Message": message_contents
    })


def _sns_confirmation_callback():
    return b'{\n    "Type": "SubscriptionConfirmation",\n    "MessageId": "165545c9-2a5c-472c-8df2-7ff2be2b3b1b",\n    "Token": "2336412f37fb687f5d51e6e241d09c805a5a57b30d712f794cc5f6a988666d92768dd60a747ba6f3beb71854e285d6ad02428b09ceece29417f1f02d609c582afbacc99c583a916b9981dd2728f4ae6fdb82efd087cc3b7849e05798d2d2785c03b0879594eeac82c01f235d0e717736",\n    "TopicArn": "arn:aws:sns:us-west-2:123456789012:MyTopic",\n    "Message": "You have chosen to subscribe to the topic arn:aws:sns:us-west-2:123456789012:MyTopic.\\nTo confirm the subscription, visit the SubscribeURL included in this message.",\n    "SubscribeURL": "https://sns.us-west-2.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-west-2:123456789012:MyTopic&Token=2336412f37fb687f5d51e6e241d09c805a5a57b30d712f794cc5f6a988666d92768dd60a747ba6f3beb71854e285d6ad02428b09ceece29417f1f02d609c582afbacc99c583a916b9981dd2728f4ae6fdb82efd087cc3b7849e05798d2d2785c03b0879594eeac82c01f235d0e717736",\n    "Timestamp": "2012-04-26T20:45:04.751Z",\n    "SignatureVersion": "1",\n    "Signature": "EXAMPLEpH+DcEwjAPg8O9mY8dReBSwksfg2S7WKQcikcNKWLQjwu6A4VbeS0QHVCkhRS7fUQvi2egU3N858fiTDN6bkkOxYDVrY0Ad8L10Hs3zH81mtnPk5uvvolIC1CXGu43obcgFxeL3khZl8IKvO61GWB6jI9b5+gLPoBc1Q=",\n    "SigningCertURL": "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-f3ecfb7224c7233fe7bb5f59f96de52f.pem"\n}'  # noqa
