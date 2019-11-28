from flask import Blueprint
from .oauth2 import authorization

bp = Blueprint('sap', __name__)


@bp.route('/sap/oauth2/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()


@bp.route('/sap/oauth2/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')
