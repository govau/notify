import uuid

from sqlalchemy import (
    Date as sql_date,
    asc,
    cast,
    desc,
    func,
)

from app import db
from app.dao import days_ago
from app.models import (
    Batch,
)


"""
def dao_get_batches_by_service_id(service_id, limit_days=None, page=1, page_size=50, statuses=None):
    if limit_days is not None:
        query_filter.append(cast(Job.created_at, sql_date) >= days_ago(limit_days))
    if statuses is not None and statuses != ['']:
        query_filter.append(
            Job.job_status.in_(statuses)
        )
    return Job.query \
        .filter(*query_filter) \
        .order_by(Job.processing_started.desc(), Job.created_at.desc()) \
        .paginate(page=page, per_page=page_size)
"""


def dao_get_batches_by_reference(reference):
    return Batch.query.filter_by(reference=reference).all()


def dao_create_batch(batch):
    if not batch.id:
        batch.id = uuid.uuid4()
    db.session.add(batch)
    db.session.commit()


def dao_update_batch(batch):
    db.session.add(batch)
    db.session.commit()