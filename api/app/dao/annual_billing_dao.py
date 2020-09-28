from app import db
from app.dao.dao_utils import (
    transactional,
)
from app.models import AnnualBilling
from app.dao.date_util import get_current_financial_year_start_year


@transactional
def dao_create_or_update_annual_billing_for_year(service_id, free_sms_fragment_limit, financial_year_start):
    result = dao_get_free_sms_fragment_limit_for_year(service_id, financial_year_start)

    if result:
        result.free_sms_fragment_limit = free_sms_fragment_limit
    else:
        result = AnnualBilling(service_id=service_id, financial_year_start=financial_year_start,
                               free_sms_fragment_limit=free_sms_fragment_limit)
    db.session.add(result)
    return result


def dao_get_annual_billing(service_id):
    return AnnualBilling.query.filter_by(
        service_id=service_id,
    ).order_by(AnnualBilling.financial_year_start).all()


@transactional
def dao_update_annual_billing_for_future_years(service_id, free_sms_fragment_limit, financial_year_start):
    AnnualBilling.query.filter(
        AnnualBilling.service_id == service_id,
        AnnualBilling.financial_year_start > financial_year_start
    ).update(
        {'free_sms_fragment_limit': free_sms_fragment_limit}
    )


def dao_get_free_sms_fragment_limit_for_year(service_id, financial_year_start=None):

    if not financial_year_start:
        financial_year_start = get_current_financial_year_start_year()

    return AnnualBilling.query.filter_by(
        service_id=service_id,
        financial_year_start=financial_year_start
    ).first()


def dao_get_all_free_sms_fragment_limit(service_id):

    return AnnualBilling.query.filter_by(
        service_id=service_id,
    ).order_by(AnnualBilling.financial_year_start).all()


def dao_insert_annual_billing_for_this_year(service, free_sms_fragment_limit):
    """
    This method is called from create_service which is wrapped in a transaction.
    """
    annual_billing = AnnualBilling(
        free_sms_fragment_limit=free_sms_fragment_limit,
        financial_year_start=get_current_financial_year_start_year(),
        service=service,
    )

    db.session.add(annual_billing)


def dao_get_free_sms_fragment_limit(service_id, financial_year_start, current_year):
    annual_billing = dao_get_free_sms_fragment_limit_for_year(service_id, financial_year_start)

    if annual_billing is not None:
        return annual_billing

    # An entry does not exist in annual_billing table for that service and year. If it is a past year,
    # we return the oldest entry.
    # If it is the current or future years, we create an entry in the db table using the newest record,
    # and return that number.  If all fails, we return InvalidRequest.
    sms_list = dao_get_all_free_sms_fragment_limit(service_id)

    if not sms_list:
        return None

    if financial_year_start is None:
        financial_year_start = current_year

    if financial_year_start < current_year:
        # return the earliest historical entry
        annual_billing = sms_list[0]   # The oldest entry
    else:
        annual_billing = sms_list[-1]  # The newest entry
        annual_billing = dao_create_or_update_annual_billing_for_year(
            service_id, annual_billing.free_sms_fragment_limit, financial_year_start
        )

    return annual_billing
