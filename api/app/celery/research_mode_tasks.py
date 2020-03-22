from datetime import datetime
import json

from flask import current_app
from requests import request, RequestException, HTTPError

from notifications_utils.s3 import s3upload

from app import notify_celery
from app.models import SMS_TYPE
from app.config import QueueNames
from app.celery.process_ses_receipts_tasks import process_ses_results_task

temp_fail = "409000003"
perm_fail = "409000002"
delivered = "409000001"

delivered_email = "delivered@simulator.notify"
perm_fail_email = "perm-fail@simulator.notify"
temp_fail_email = "temp-fail@simulator.notify"


def send_sms_response(provider, notification_id, to):
    if provider == "sap":
        headers = {"Content-type": "application/json"}
        body = sap_callback(notification_id, to)
    elif provider == "telstra":
        headers = {"Content-type": "application/json"}
        body = telstra_callback(notification_id, to)
    elif provider == "twilio":
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        body = twilio_callback(notification_id, to)
    else:
        raise ValueError("Invalid provider: {}".format(provider))

    make_request(SMS_TYPE, provider, notification_id, body, headers)


def send_email_response(reference, to):
    if to == perm_fail_email:
        body = ses_hard_bounce_callback(reference)
    elif to == temp_fail_email:
        body = ses_soft_bounce_callback(reference)
    else:
        body = ses_notification_callback(reference)

    process_ses_results_task.apply_async([body], queue=QueueNames.RESEARCH_MODE)


def make_request(notification_type, provider, notification_id, data, headers):
    api_call = "{}/notifications/{}/{}/{}".format(current_app.config["API_HOST_NAME"], notification_type, provider, notification_id)

    try:
        response = request(
            "POST",
            api_call,
            headers=headers,
            data=data,
            timeout=60
        )
        response.raise_for_status()
    except RequestException as e:
        api_error = HTTPError(e)
        current_app.logger.error(
            "API {} request on {} failed with {}".format(
                "POST",
                api_call,
                api_error.response
            )
        )
        raise api_error
    finally:
        current_app.logger.info("Mocked provider callback request finished")
    return response.json()


def sap_callback(notification_id, to):
    if to.strip().endswith(temp_fail):
        status = "ERROR"  # We don't seem to have a SAP state for temp fail
    elif to.strip().endswith(perm_fail):
        status = "ERROR"
    else:
        status = "DELIVERED"

    return json.dumps({
        "messageId": "XXXX",
        "recipient": to,
        "status": status,
    })


def telstra_callback(notification_id, to):
    if to.strip().endswith(temp_fail):
        status = "REJECTED"
    elif to.strip().endswith(perm_fail):
        status = "UNDVBL"
    else:
        status = "DELIVRD"

    return json.dumps({
        "messageId": "XXXX",
        "to": to,
        "deliveryStatus": status,
    })


def twilio_callback(notification_id, to):
    if to.strip().endswith(temp_fail):
        status = "failed"
    elif to.strip().endswith(perm_fail):
        status = "undelivered"
    else:
        status = "delivered"
    return {
        "AccountSid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "ApiVersion": "2010-04-01",
        "From": "+14155552345",
        "MessageSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "MessageStatus": status,
        "SmsSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "SmsStatus": status,
        "To": to,
    }


@notify_celery.task(bind=True, name="create-fake-letter-response-file", max_retries=5, default_retry_delay=300)
def create_fake_letter_response_file(self, reference):
    now = datetime.utcnow()
    dvla_response_data = '{}|Sent|0|Sorted'.format(reference)
    upload_file_name = 'NOTIFY-{}-RSP.TXT'.format(now.strftime('%Y%m%d%H%M%S'))

    s3upload(
        filedata=dvla_response_data,
        region=current_app.config['AWS_REGION'],
        bucket_name=current_app.config['DVLA_RESPONSE_BUCKET_NAME'],
        file_location=upload_file_name
    )
    current_app.logger.info("Fake DVLA response file {}, content [{}], uploaded to {}, created at {}".format(
        upload_file_name, dvla_response_data, current_app.config['DVLA_RESPONSE_BUCKET_NAME'], now))

    # on development we can't trigger SNS callbacks so we need to manually hit the DVLA callback endpoint
    if current_app.config['NOTIFY_ENVIRONMENT'] == 'development':
        make_request('letter', 'dvla', reference, _fake_sns_s3_callback(upload_file_name), None)


def _fake_sns_s3_callback(filename):
    message_contents = '{"Records":[{"s3":{"object":{"key":"%s"}}}]}' % (filename)  # noqa
    return json.dumps({
        "Type": "Notification",
        "MessageId": "some-message-id",
        "Message": message_contents
    })


def ses_notification_callback(reference):
    ses_message_body = {
        'delivery': {
            'processingTimeMillis': 2003,
            'recipients': ['success@simulator.amazonses.com'],
            'remoteMtaIp': '123.123.123.123',
            'reportingMTA': 'a7-32.smtp-out.eu-west-1.amazonses.com',
            'smtpResponse': '250 2.6.0 Message received',
            'timestamp': '2017-11-17T12:14:03.646Z'
        },
        'mail': {
            'commonHeaders': {
                'from': ['TEST <TEST@notify.works>'],
                'subject': 'lambda test',
                'to': ['success@simulator.amazonses.com']
            },
            'destination': ['success@simulator.amazonses.com'],
            'headers': [
                {
                    'name': 'From',
                    'value': 'TEST <TEST@notify.works>'
                },
                {
                    'name': 'To',
                    'value': 'success@simulator.amazonses.com'
                },
                {
                    'name': 'Subject',
                    'value': 'lambda test'
                },
                {
                    'name': 'MIME-Version',
                    'value': '1.0'
                },
                {
                    'name': 'Content-Type',
                    'value': 'multipart/alternative; boundary="----=_Part_617203_1627511946.1510920841645"'
                }
            ],
            'headersTruncated': False,
            'messageId': reference,
            'sendingAccountId': '12341234',
            'source': '"TEST" <TEST@notify.works>',
            'sourceArn': 'arn:aws:ses:eu-west-1:12341234:identity/notify.works',
            'sourceIp': '0.0.0.1',
            'timestamp': '2017-11-17T12:14:01.643Z'
        },
        'notificationType': 'Delivery'
    }

    return {
        'Type': 'Notification',
        'MessageId': '8e83c020-1234-1234-1234-92a8ee9baa0a',
        'TopicArn': 'arn:aws:sns:eu-west-1:12341234:ses_notifications',
        'Subject': None,
        'Message': json.dumps(ses_message_body),
        'Timestamp': '2017-11-17T12:14:03.710Z',
        'SignatureVersion': '1',
        'Signature': '[REDACTED]',
        'SigningCertUrl': 'https://sns.eu-west-1.amazonaws.com/SimpleNotificationService-[REDACTED].pem',
        'UnsubscribeUrl': 'https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=[REACTED]',
        'MessageAttributes': {}
    }


def ses_hard_bounce_callback(reference):
    return _ses_bounce_callback(reference, 'Permanent')


def ses_soft_bounce_callback(reference):
    return _ses_bounce_callback(reference, 'Temporary')


def _ses_bounce_callback(reference, bounce_type):
    ses_message_body = {
        'bounce': {
            'bounceSubType': 'General',
            'bounceType': bounce_type,
            'bouncedRecipients': [{
                'action': 'failed',
                'diagnosticCode': 'smtp; 550 5.1.1 user unknown',
                'emailAddress': 'bounce@simulator.amazonses.com',
                'status': '5.1.1'
            }],
            'feedbackId': '0102015fc9e676fb-12341234-1234-1234-1234-9301e86a4fa8-000000',
            'remoteMtaIp': '123.123.123.123',
            'reportingMTA': 'dsn; a7-31.smtp-out.eu-west-1.amazonses.com',
            'timestamp': '2017-11-17T12:14:05.131Z'
        },
        'mail': {
            'commonHeaders': {
                'from': ['TEST <TEST@notify.works>'],
                'subject': 'ses callback test',
                'to': ['bounce@simulator.amazonses.com']
            },
            'destination': ['bounce@simulator.amazonses.com'],
            'headers': [
                {
                    'name': 'From',
                    'value': 'TEST <TEST@notify.works>'
                },
                {
                    'name': 'To',
                    'value': 'bounce@simulator.amazonses.com'
                },
                {
                    'name': 'Subject',
                    'value': 'lambda test'
                },
                {
                    'name': 'MIME-Version',
                    'value': '1.0'
                },
                {
                    'name': 'Content-Type',
                    'value': 'multipart/alternative; boundary="----=_Part_596529_2039165601.1510920843367"'
                }
            ],
            'headersTruncated': False,
            'messageId': reference,
            'sendingAccountId': '12341234',
            'source': '"TEST" <TEST@notify.works>',
            'sourceArn': 'arn:aws:ses:eu-west-1:12341234:identity/notify.works',
            'sourceIp': '0.0.0.1',
            'timestamp': '2017-11-17T12:14:03.000Z'
        },
        'notificationType': 'Bounce'
    }
    return {
        'Type': 'Notification',
        'MessageId': '36e67c28-1234-1234-1234-2ea0172aa4a7',
        'TopicArn': 'arn:aws:sns:eu-west-1:12341234:ses_notifications',
        'Subject': None,
        'Message': json.dumps(ses_message_body),
        'Timestamp': '2017-11-17T12:14:05.149Z',
        'SignatureVersion': '1',
        'Signature': '[REDACTED]',  # noqa
        'SigningCertUrl': 'https://sns.eu-west-1.amazonaws.com/SimpleNotificationService-[REDACTED]].pem',
        'UnsubscribeUrl': 'https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=[REDACTED]]',
        'MessageAttributes': {}
    }
