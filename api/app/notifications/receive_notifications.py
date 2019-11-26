import os
from datetime import datetime

from flask import Blueprint, current_app, request, abort, json
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator

from notifications_utils.recipients import try_validate_and_format_phone_number

from app import statsd_client
from app.celery import tasks
from app.config import QueueNames
from app.dao.services_dao import dao_fetch_service_by_inbound_number
from app.dao.inbound_sms_dao import dao_create_inbound_sms
from app.models import InboundSms, INBOUND_SMS_TYPE, SMS_TYPE
from app.errors import register_errors
from app.sap.oauth2 import require_oauth

receive_notifications_blueprint = Blueprint('receive_notifications', __name__)
register_errors(receive_notifications_blueprint)


@receive_notifications_blueprint.route('/notifications/sms/receive/sap', methods=['POST'])
@require_oauth(scope=None)
def receive_sap_sms():
    response = MessagingResponse()

    data = json.loads(request.data)

    service = fetch_potential_service(data['originatingAddress'], 'sap')

    if not service:
        # Since this is an issue with our service <-> number mapping, or no
        # inbound_sms service permission we should still tell SAP that we
        # received it successfully.
        return str(response), 200

    statsd_client.incr('inbound.sap.successful')

    inbound = create_inbound_sms_object(service,
                                        content=data["message"],
                                        from_number=data['msisdn'],
                                        provider_ref=data["messageId"],
                                        provider_name="sap")

    tasks.send_inbound_sms_to_service.apply_async([str(inbound.id), str(service.id)], queue=QueueNames.NOTIFY)

    current_app.logger.debug('{} received inbound SMS with reference {} from SAP'.format(
        service.id,
        inbound.provider_reference,
    ))

    return str(response), 200


@receive_notifications_blueprint.route('/notifications/sms/receive/twilio', methods=['POST'])
def receive_twilio_sms():
    response = MessagingResponse()

    auth = request.authorization

    if not auth:
        current_app.logger.warning("Inbound sms (Twilio) no auth header")
        abort(401)
    elif auth.username not in current_app.config['TWILIO_INBOUND_SMS_USERNAMES'] or auth.password not in current_app.config['TWILIO_INBOUND_SMS_PASSWORDS']:
        current_app.logger.warning("Inbound sms (Twilio) incorrect username ({}) or password".format(auth.username))
        abort(403)

    # Locally, when using ngrok the URL comes in without HTTPS so force it
    # otherwise the Twilio signature validator will fail.
    url = request.url.replace("http://", "https://")
    post_data = request.form
    twilio_signature = request.headers.get('X-Twilio-Signature')

    validator = RequestValidator(os.getenv('TWILIO_AUTH_TOKEN'))

    if not validator.validate(url, post_data, twilio_signature):
        current_app.logger.warning("Inbound sms (Twilio) signature did not match request")
        abort(400)

    service = fetch_potential_service(post_data['To'], 'twilio')

    if not service:
        # Since this is an issue with our service <-> number mapping, or no
        # inbound_sms service permission we should still tell Twilio that we
        # received it successfully.
        return str(response), 200

    statsd_client.incr('inbound.twilio.successful')

    inbound = create_inbound_sms_object(service,
                                        content=post_data["Body"],
                                        from_number=post_data['From'],
                                        provider_ref=post_data["MessageSid"],
                                        provider_name="twilio")

    tasks.send_inbound_sms_to_service.apply_async([str(inbound.id), str(service.id)], queue=QueueNames.NOTIFY)

    current_app.logger.debug('{} received inbound SMS with reference {} from Twilio'.format(
        service.id,
        inbound.provider_reference,
    ))

    return str(response), 200


def create_inbound_sms_object(service, content, from_number, provider_ref, provider_name):
    user_number = try_validate_and_format_phone_number(
        from_number,
        international=True,
        log_msg='Invalid from_number received'
    )

    inbound = InboundSms(
        service=service,
        notify_number=service.get_inbound_number(),
        user_number=user_number,
        provider_date=datetime.utcnow(),
        provider_reference=provider_ref,
        content=content,
        provider=provider_name
    )
    dao_create_inbound_sms(inbound)
    return inbound


def fetch_potential_service(inbound_number, provider_name):
    service = dao_fetch_service_by_inbound_number(inbound_number)

    if not service:
        current_app.logger.error('Inbound number "{}" from {} not associated with a service'.format(
            inbound_number, provider_name
        ))
        statsd_client.incr('inbound.{}.failed'.format(provider_name))
        return False

    if not has_inbound_sms_permissions(service.permissions):
        current_app.logger.error(
            'Service "{}" does not allow inbound SMS'.format(service.id))
        return False

    return service


def has_inbound_sms_permissions(permissions):
    str_permissions = [p.permission for p in permissions]
    return set([INBOUND_SMS_TYPE, SMS_TYPE]).issubset(set(str_permissions))
