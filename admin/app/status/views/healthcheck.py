from flask import current_app, jsonify, request
from notify.errors import HTTPError

from app import status_api_client, version
from app.status import status


@status.route('/_status', methods=['GET'])
def show_status():
    if request.args.get('elb', None):
        return jsonify(status="ok"), 200
    else:
        try:
            api_status = status_api_client.get_status()
        except HTTPError as e:
            current_app.logger.exception("API failed to respond")
            return jsonify(status="error", message=str(e.message)), 500
        return jsonify(
            status="ok",
            api=api_status,
            commit_sha=version.__commit_sha__,
            build_number=version.__build_number__,
            build_time=version.__time__), 200
