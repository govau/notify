from app import db
from app.dao.dao_utils import transactional
from app.models import CallbackFailure


@transactional
def dao_create_callback_failure(callback_failure):
    db.session.add(callback_failure)


def dao_get_callback_failures_by_service_id(service_id):
    return CallbackFailure.query.join(CallbackFailure.notification).filter_by(service_id=service_id)
