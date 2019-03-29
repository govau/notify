from flask import (
    jsonify,
    Blueprint,
    request,
    current_app
)

from app.service.sender import send_notification_to_notify_support

support = Blueprint('support', __name__)


@support.route('/support', methods=['POST'])
def support_request():
    send_notification_to_notify_support(current_app.config['SUPPORT_QUESTION_FEEDBACK'], request.get_json())
    return jsonify(status="ok"), 200
