from sqlalchemy import func, desc, Integer, and_
from app.utils import get_sydney_midnight_in_utc
from app import db
from app.dao.date_util import (
    get_financial_year_start,
    get_financial_year_for_datetime
)

from app.models import (
    FactBilling,
    Service,
    LETTER_TYPE,
    SMS_TYPE,
    Rate,
    LetterRate,
    NotificationHistory,
    EMAIL_TYPE,
    AnnualBilling,
)


def fetch_sms_free_allowance_remainder(start_date):
    # ASSUMPTION: AnnualBilling has been populated for year.
    billing_year = get_financial_year_for_datetime(start_date)
    start_of_year = get_financial_year_start(billing_year)

    billable_units = func.coalesce(func.sum(FactBilling.billable_units * FactBilling.rate_multiplier), 0)

    query = db.session.query(
        AnnualBilling.service_id.label("service_id"),
        AnnualBilling.free_sms_fragment_limit,
        billable_units.label('billable_units'),
        func.greatest((AnnualBilling.free_sms_fragment_limit - billable_units).cast(Integer), 0).label('sms_remainder')
    ).outerjoin(
        # if there are no ft_billing rows for a service we still want to return the annual billing so we can use the
        # free_sms_fragment_limit)
        FactBilling, and_(
            AnnualBilling.service_id == FactBilling.service_id,
            FactBilling.aet_date >= start_of_year,
            FactBilling.aet_date < start_date,
            FactBilling.notification_type == SMS_TYPE,
        )
    ).filter(
        AnnualBilling.financial_year_start == billing_year,
    ).group_by(
        AnnualBilling.service_id,
        AnnualBilling.free_sms_fragment_limit,
    )
    return query


def fetch_sms_billing_for_all_services(start_date, end_date):

    # ASSUMPTION: AnnualBilling has been populated for year.
    free_allowance_remainder = fetch_sms_free_allowance_remainder(start_date).subquery()

    sms_notifications_sent = func.sum(FactBilling.notifications_sent)
    sms_billable_units = func.sum(FactBilling.billable_units * FactBilling.rate_multiplier)
    sms_remainder = func.coalesce(
        free_allowance_remainder.c.sms_remainder,
        free_allowance_remainder.c.free_sms_fragment_limit
    )
    chargeable_sms = func.greatest(sms_billable_units - sms_remainder, 0)
    sms_cost = chargeable_sms * FactBilling.rate

    query = db.session.query(
        Service.name.label('service_name'),
        Service.id.label('service_id'),
        free_allowance_remainder.c.free_sms_fragment_limit,
        FactBilling.rate.label('sms_rate'),
        sms_remainder.label('sms_remainder'),
        sms_billable_units.label('sms_billable_units'),
        chargeable_sms.label('chargeable_billable_sms'),
        sms_notifications_sent.label('sms_notifications_sent'),
        sms_cost.label('sms_cost'),
    ).select_from(
        Service
    ).outerjoin(
        free_allowance_remainder, Service.id == free_allowance_remainder.c.service_id
    ).join(
        FactBilling, FactBilling.service_id == Service.id,
    ).filter(
        FactBilling.aet_date >= start_date,
        FactBilling.aet_date <= end_date,
        FactBilling.notification_type == SMS_TYPE,
    ).group_by(
        Service.id,
        Service.name,
        free_allowance_remainder.c.free_sms_fragment_limit,
        free_allowance_remainder.c.sms_remainder,
        FactBilling.rate,
    ).order_by(
        Service.name
    )

    return query.all()


def fetch_usage_for_all_services(start_date, end_date):
    billable_units = func.sum(FactBilling.billable_units * FactBilling.rate_multiplier)

    query = db.session.query(
        Service.name.label('service_name'),
        Service.id.label('service_id'),
        FactBilling.notification_type.label('notification_type'),
        FactBilling.rate.label('rate'),
        FactBilling.rate_multiplier.label('rate_multiplier'),
        func.sum(FactBilling.notifications_sent).label('notifications_sent'),
        func.sum(FactBilling.billable_units).label('billable_units_sent'),
        billable_units.label('total_billable_units'),
    ).select_from(
        Service
    ).join(
        FactBilling, FactBilling.service_id == Service.id,
    ).filter(
        FactBilling.aet_date >= start_date,
        FactBilling.aet_date <= end_date,
    ).group_by(
        Service.id,
        Service.name,
        FactBilling.notification_type,
        FactBilling.rate_multiplier,
        FactBilling.rate,
    ).order_by(
        Service.id
    )

    return query.all()


def get_rates_for_billing():
    non_letter_rates = Rate.query.order_by(desc(Rate.valid_from)).all()
    letter_rates = LetterRate.query.order_by(desc(LetterRate.start_date)).all()
    return non_letter_rates, letter_rates


def get_service_ids_that_need_billing_populated(start_date, end_date):
    return db.session.query(
        NotificationHistory.service_id
    ).filter(
        NotificationHistory.created_at >= start_date,
        NotificationHistory.created_at <= end_date,
        NotificationHistory.notification_type.in_([SMS_TYPE, EMAIL_TYPE, LETTER_TYPE]),
        NotificationHistory.billable_units != 0
    ).distinct().all()


def get_rate(
    non_letter_rates, letter_rates, notification_type, date, crown=None, letter_page_count=None, post_class='second'
):
    start_of_day = get_sydney_midnight_in_utc(date)

    if notification_type == LETTER_TYPE:
        if letter_page_count == 0:
            return 0
        return next(
            r.rate
            for r in letter_rates if (
                start_of_day >= r.start_date and
                crown == r.crown and
                letter_page_count == r.sheet_count and
                post_class == r.post_class
            )
        )
    elif notification_type == SMS_TYPE:
        return next(
            r.rate
            for r in non_letter_rates if (
                notification_type == r.notification_type and
                start_of_day >= r.valid_from
            )
        )
    else:
        return 0
