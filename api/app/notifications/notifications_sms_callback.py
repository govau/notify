from flask import Blueprint
from flask import current_app
from flask import request, jsonify

from app import clients
from app.models import SMS_TYPE
from app.clients.sms import PollableSMSClient

from app.errors import InvalidRequest, register_errors
from app.notifications.process_client_response import validate_callback_data, process_sms_client_response
from app.sap.oauth2 import require_oauth
from app.dao.notifications_dao import get_notification_by_reference

sms_callback_blueprint = Blueprint("sms_callback", __name__, url_prefix="/notifications/sms")
register_errors(sms_callback_blueprint)


@sms_callback_blueprint.route('/sap/<notification_id>', methods=['POST'])
@require_oauth(scope=None)
def process_sap_response(notification_id):
    client_name = 'sap'
    data = request.json
    errors = validate_callback_data(data=data,
                                    fields=['messageId', 'status'],
                                    client_name=client_name)
    if errors:
        raise InvalidRequest(errors, status_code=400)

    success, errors = process_sms_client_response(status=str(data.get('status')),
                                                  provider_reference=notification_id,
                                                  client_name=client_name)

    redacted_data = data.copy()
    redacted_data.pop("recipient")
    redacted_data.pop("message")
    current_app.logger.debug(
        "Full delivery response from {} for notification: {}\n{}".format(client_name, notification_id, redacted_data))
    if errors:
        raise InvalidRequest(errors, status_code=400)
    else:
        return jsonify(result='success', message=success), 200


@sms_callback_blueprint.route('/telstra/<notification_id>', methods=['POST'])
def process_telstra_response(notification_id):
    client_name = 'telstra'
    data = request.json

    errors = validate_callback_data(
        data=data,
        fields=['messageId', 'deliveryStatus'],
        client_name=client_name)

    if errors:
        raise InvalidRequest(errors, status_code=400)

    success, errors = process_sms_client_response(
        status=str(data.get('deliveryStatus')),
        provider_reference=notification_id,
        client_name=client_name)

    redacted_data = data.copy()
    redacted_data.pop("to")
    current_app.logger.debug(
        "Full delivery response from {} for notification: {}\n{}".format(client_name, notification_id, redacted_data))

    if errors:
        raise InvalidRequest(errors, status_code=400)

    return jsonify(result='success', message=success), 200


@sms_callback_blueprint.route('/twilio/<notification_id>', methods=['POST'])
def process_twilio_response(notification_id):
    client_name = 'twilio'

    data = request.values
    errors = validate_callback_data(
        data=data,
        fields=['MessageStatus', 'MessageSid'],
        client_name=client_name
    )

    if errors:
        raise InvalidRequest(errors, status_code=400)

    success, errors = process_sms_client_response(
        status=data.get('MessageStatus'),
        provider_reference=notification_id,
        client_name=client_name
    )

    redacted_data = dict(data.items())
    redacted_data.pop('To', None)
    current_app.logger.debug(
        "Full delivery response from {} for notification: {}\n{}".format(client_name, notification_id, redacted_data))
    if errors:
        raise InvalidRequest(errors, status_code=400)
    else:
        return jsonify(result='success', message=success), 200


# this will provide a status checker for a given notification type and provider
# pair.
#
# the status checker is a generator that yields out (reference, status) pairs
# that can then be recorded against our internal notifications
def get_message_status_checker(notification_type, provider):
    def check_nothing(*args, **kwargs):
        current_app.logger.debug(f"get_message_status_checker: no status checker available for type {notification_type}")
        yield from ()

    def status_checker(client):
        def check_status(*args, **kwargs):
            if not isinstance(client, PollableSMSClient):
                current_app.logger.debug(f"get_message_status_checker: provider {provider} does not support status checks")
                return

            yield from client.check_message_status(*args, **kwargs)
        return check_status

    if notification_type == SMS_TYPE:
        client = clients.get_sms_client(provider)
        return status_checker(client)

    return check_nothing


# record an updated status for a notification using its external reference and
# our common callback logic
def record_notification_status(provider, reference, response):
    notification = get_notification_by_reference(reference)

    return process_sms_client_response(
        status=response,
        provider_reference=str(notification.id),
        client_name=provider
    )
