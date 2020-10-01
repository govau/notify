from sqlalchemy import func, case, Integer, Date, cast, and_, column, literal
from app import db
from app.dao.date_util import (
    get_financial_year_start,
    get_financial_year_for_datetime,
    get_current_financial_year_start_year,
)
import datetime
from app.models import (
    FactBilling,
    Service,
    SMS_TYPE,
    EMAIL_TYPE,
    AnnualBilling,
)
from app.dao.annual_billing_dao import dao_get_free_sms_fragment_limit


DOMESTIC_UNIT_RATE = 0.06
INTERNATIONAL_UNIT_RATE = 0.13
FRAGMENT_UNIT_RATE = DOMESTIC_UNIT_RATE


def get_internationalised_billable_units():
    return func.coalesce(
        FactBilling.billable_units *
        case([
            (FactBilling.international == 't', 2.167),
            (FactBilling.international == 'f', 1),
        ]),
        0
    )


# TODO: migrate to this
def _fetch_sms_free_allowance_for_financial_year(service_id, year):
    """
    We use one rate for the entire financial year.
    Take the most recently touched entry
    """
    modified_at = func.greatest(AnnualBilling.created_at, AnnualBilling.updated_at)

    query = db.session.query(
        AnnualBilling.service_id,
        AnnualBilling.financial_year_start,
        AnnualBilling.free_sms_fragment_limit,
        modified_at.label('modified_at'),
    ).distinct(
        AnnualBilling.service_id,
        AnnualBilling.financial_year_start,
    ).filter(
        AnnualBilling.service_id == service_id,
        AnnualBilling.financial_year_start == year,
    ).order_by(
        AnnualBilling.service_id,
        AnnualBilling.financial_year_start,
        modified_at.desc(),
    )
    return query.one().free_sms_fragment_limit


def fetch_sms_free_allowance_for_financial_year(service_id, year):
    # this might come back as none but it's not recoverable. fail here or somewhere else
    results = dao_get_free_sms_fragment_limit(service_id, year, get_current_financial_year_start_year())
    return results.free_sms_fragment_limit


def fetch_sms_free_allowance_remainder(start_date):
    # ASSUMPTION: AnnualBilling has been populated for year.
    billing_year = get_financial_year_for_datetime(start_date)
    start_of_year = get_financial_year_start(billing_year)

    billable_units = func.sum(get_internationalised_billable_units())

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


def get_financial_year_range(year):
    start_date = datetime.datetime.strptime(f'{year}-07-01', "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(f'{year+1}-06-30', "%Y-%m-%d").date()
    return start_date, end_date


def total(e):
    return func.sum(func.coalesce(e, 0))


def dao_get_priced_billing_data():
    aet_month = cast(func.date_trunc('month', FactBilling.aet_date), Date())

    international_units = case([
        (FactBilling.international == 't', FactBilling.billable_units),
        (FactBilling.international == 'f', 0),
    ])

    domestic_units = case([
        (FactBilling.international == 't', 0),
        (FactBilling.international == 'f', FactBilling.billable_units),
    ])

    cost = func.coalesce(
        FactBilling.billable_units *
        case([
            (FactBilling.international == 't', INTERNATIONAL_UNIT_RATE),
            (FactBilling.international == 'f', DOMESTIC_UNIT_RATE),
        ]),
        0
    )

    return db.session.query(
        aet_month.label('aet_month'),
        FactBilling.aet_date,
        FactBilling.template_id,
        FactBilling.service_id,
        FactBilling.billable_units,
        FactBilling.notifications_sent,
        FactBilling.notification_type,
        domestic_units.label('domestic_units'),
        international_units.label('international_units'),
        cost.label('cost'),
    ).select_from(
        FactBilling
    ).order_by(
        FactBilling.service_id,
        aet_month,
    )


def fetch_annual_billing(service_id, year):
    start_date, end_date = get_financial_year_range(year)
    fragments_free_limit = literal(fetch_sms_free_allowance_for_financial_year(service_id, year))
    query = dao_get_priced_billing_data().filter(
        FactBilling.service_id == service_id,
        FactBilling.aet_date >= start_date,
        FactBilling.aet_date <= end_date,
    )

    # break down usage by month with empty gaps by generating a series
    months_series = func.generate_series(start_date, end_date, '1 month').alias('month')
    months_series_c = column('month').cast(Date()).label('month')
    query_cte = query.cte()

    # calculate in credits in order to work backwards to get available units
    # after removing cost usage
    credits_free = fragments_free_limit * FRAGMENT_UNIT_RATE

    # coalesce and sum these totals by month
    cost = total(query_cte.c.cost)
    notifications = total(query_cte.c.notifications_sent)
    notifications_email_ = func.sum(query_cte.c.notifications_sent).filter(query_cte.c.notification_type == EMAIL_TYPE)
    notifications_sms_ = func.sum(query_cte.c.notifications_sent).filter(query_cte.c.notification_type == SMS_TYPE)
    notifications_email = func.coalesce(notifications_email_, 0)
    notifications_sms = func.coalesce(notifications_sms_, 0)

    fragments_domestic = total(query_cte.c.domestic_units)
    fragments_international = total(query_cte.c.international_units)

    # cumulative figures for entire year
    cost_cumulative = func.sum(cost).over(order_by=months_series_c)
    cost_starting = cost_cumulative - cost
    credits_remaining = func.greatest(credits_free - cost_cumulative, 0)
    credits_available = func.greatest(credits_free - cost_starting, 0)
    cost_chargeable = func.greatest(cost - credits_available, 0)
    cost_chargeable_cumulative = func.greatest(cost_cumulative - credits_free, 0)

    credits_used = func.least(cost, credits_available)
    units = cost / FRAGMENT_UNIT_RATE
    units_cumulative = cost_cumulative / FRAGMENT_UNIT_RATE
    units_chargeable = cost_chargeable / FRAGMENT_UNIT_RATE
    units_free_used = credits_used / FRAGMENT_UNIT_RATE
    units_free_available = credits_available / FRAGMENT_UNIT_RATE
    units_free_remaining = credits_remaining / FRAGMENT_UNIT_RATE
    units_chargeable_cumulative = cost_chargeable_cumulative / FRAGMENT_UNIT_RATE

    gapfilled_query = db.session.query(
        months_series_c,
        fragments_free_limit.label('fragments_free_limit'),
        fragments_domestic.label('fragments_domestic'),
        fragments_international.label('fragments_international'),

        notifications.label('notifications'),
        notifications_sms.label('notifications_sms'),
        notifications_email.label('notifications_email'),

        cost.label('cost'),
        cost_chargeable.label('cost_chargeable'),
        cost_cumulative.label('cost_cumulative'),
        cost_chargeable_cumulative.label('cost_chargeable_cumulative'),

        units.label('units'),
        units_cumulative.label('units_cumulative'),
        units_chargeable.label('units_chargeable'),
        units_chargeable_cumulative.label('units_chargeable_cumulative'),
        units_free_available.label('units_free_available'),
        units_free_remaining.label('units_free_remaining'),
        units_free_used.label('units_free_used'),

        literal(DOMESTIC_UNIT_RATE * 100).label('unit_rate_domestic'),
        literal(INTERNATIONAL_UNIT_RATE * 100).label('unit_rate_international'),
    ).select_from(
        months_series,
    ).outerjoin(
        query_cte, query_cte.c.aet_month == months_series_c,
    ).group_by(
        months_series_c,
    ).order_by(
        months_series_c
    )
    return gapfilled_query


def fetch_sms_billing_for_all_services(start_date, end_date):
    # ASSUMPTION: AnnualBilling has been populated for year.
    free_allowance_remainder = fetch_sms_free_allowance_remainder(start_date).subquery()
    notifications_sent = func.sum(FactBilling.notifications_sent)
    billable_units = func.sum(FactBilling.billable_units)
    billable_units_adjusted = func.sum(get_internationalised_billable_units())

    international_units = func.sum(
        case([
            (FactBilling.international == 't', FactBilling.billable_units),
            (FactBilling.international == 'f', 0),
        ])
    )

    domestic_units = func.sum(
        case([
            (FactBilling.international == 't', 0),
            (FactBilling.international == 'f', FactBilling.billable_units),
        ])
    )

    chargeable_units = func.greatest(billable_units_adjusted - free_allowance_remainder.c.sms_remainder, 0)
    total_cost = chargeable_units * FactBilling.rate

    query = db.session.query(
        Service.name.label('service_name'),
        Service.id.label('service_id'),
        free_allowance_remainder.c.sms_remainder,
        free_allowance_remainder.c.free_sms_fragment_limit,
        FactBilling.rate.label('sms_rate'),
        notifications_sent.label('notifications_sent'),
        billable_units.label('billable_units'),
        billable_units_adjusted.label('billable_units_adjusted'),
        international_units.label('international_units'),
        domestic_units.label('domestic_units'),
        chargeable_units.label('chargeable_units'),
        total_cost.label('total_cost'),
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
