from flask import jsonify, redirect, render_template, session, url_for
from flask_login import login_required
from notify.errors import HTTPError
from notifications_utils.recipients import (
    e164_to_phone_number,
    format_phone_number_human_readable,
    validate_and_format_phone_number_and_allow_international,
)
from notifications_utils.template import SMSPreviewTemplate

from app import notification_api_client, service_api_client
from app.main import main
from app.main.forms import SearchTemplatesForm
from app.utils import user_has_permissions


@main.route("/services/<service_id>/conversation/<notification_id>")
@login_required
@user_has_permissions('view_activity')
def conversation(service_id, notification_id):

    user_number = get_user_number(service_id, notification_id)

    return render_template(
        'views/conversations/conversation.html',
        user_number=user_number,
        partials=get_conversation_partials(service_id, user_number),
        updates_url=url_for('.conversation_updates', service_id=service_id, notification_id=notification_id),
        notification_id=notification_id,
    )


@main.route("/services/<service_id>/conversation/<notification_id>.json")
@login_required
@user_has_permissions('view_activity')
def conversation_updates(service_id, notification_id):

    return jsonify(get_conversation_partials(
        service_id,
        get_user_number(service_id, notification_id)
    ))


@main.route("/services/<service_id>/conversation/<notification_id>/reply-with")
@login_required
@user_has_permissions('send_messages')
def conversation_reply(
    service_id,
    notification_id,
):

    templates = [
        template
        for template in service_api_client.get_service_templates(service_id)['data']
        if template['template_type'] == 'sms'
    ]

    return render_template(
        'views/templates/choose-reply.html',
        templates=templates,
        show_search_box=(len(templates) > 7),
        template_type='sms',
        search_form=SearchTemplatesForm(),
        notification_id=notification_id,
    )


@main.route("/services/<service_id>/conversation/<notification_id>/reply-with/<template_id>")
@login_required
@user_has_permissions('send_messages')
def conversation_reply_with_template(
    service_id,
    notification_id,
    template_id,
):

    session['recipient'] = get_user_number(service_id, notification_id)
    session['placeholders'] = {'phone number': session['recipient']}

    return redirect(url_for(
        'main.send_one_off_step',
        service_id=service_id,
        template_id=template_id,
        step_index=1,
    ))


def get_conversation_partials(service_id, user_number):

    return {
        'messages': render_template(
            'views/conversations/messages.html',
            conversation=get_sms_thread(service_id, user_number),
        )
    }


def get_user_number(service_id, notification_id):
    try:
        number_e164 = service_api_client.get_inbound_sms_by_id(service_id, notification_id)['user_number']
    except HTTPError:
        notification = notification_api_client.get_notification(service_id, notification_id)

        number_e164 = notification['normalised_to']

        # For old records normalised_to may be empty or it may be stored in the
        # old format (without storing the leading plus sign). If this is the
        # case, use the to field instead and create the E.164 format on the fly.
        if not number_e164 or not number_e164.startswith('+'):
            try:
                number_e164 = validate_and_format_phone_number_and_allow_international(notification['to'])
            except Exception:
                return notification['to']

    number = e164_to_phone_number(number_e164)

    return format_phone_number_human_readable(number)


def get_sms_thread(service_id, user_number):

    for notification in sorted((
        notification_api_client.get_notifications_for_service(service_id,
                                                              to=user_number,
                                                              template_type='sms')['notifications'] +
        service_api_client.get_inbound_sms(service_id, user_number=user_number)['data']
    ), key=lambda notification: notification['created_at']):

        is_inbound = ('notify_number' in notification)
        redact_personalisation = not is_inbound and notification['template']['redact_personalisation']

        if redact_personalisation:
            notification['personalisation'] = {}

        yield {
            'inbound': is_inbound,
            'content': SMSPreviewTemplate(
                {
                    'content': (
                        notification['content'] if is_inbound else
                        notification['template']['content']
                    )
                },
                notification.get('personalisation'),
                downgrade_non_gsm_characters=(not is_inbound),
                redact_missing_personalisation=redact_personalisation,
            ),
            'created_at': notification['created_at'],
            'status': notification.get('status'),
            'id': notification['id'],
        }
