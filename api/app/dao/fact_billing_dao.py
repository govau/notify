from sqlalchemy import func, case, Integer, and_
from app import db
from app.dao.date_util import (
    get_financial_year_start,
    get_financial_year_for_datetime
)
from app.models import (
    FactBilling,
    Service,
    SMS_TYPE,
    AnnualBilling,
)


def get_internationalised_billable_units():
    return func.coalesce(
        FactBilling.billable_units *
        case([
            (FactBilling.international == 't', 2.167),
            (FactBilling.international == 'f', 1),
        ]),
        0
    )


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
