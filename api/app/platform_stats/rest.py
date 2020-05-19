from datetime import datetime

from flask import Blueprint, jsonify, request

from app.errors import register_errors
from app.platform_stats.platform_stats_schema import platform_stats_request
from app.dao.services_dao import (
    fetch_aggregate_stats_by_date_range_for_all_services
)
from app.service.statistics import format_admin_stats
from app.schema_validation import validate
from app.utils import convert_utc_to_aet
from app.dao.fact_billing_dao import (
    fetch_monthly_billing_for_year,
    fetch_billing_totals_for_year,
    fetch_sms_billing_for_all_services,
)
from app.billing.billing_schemas import (
    create_or_update_free_sms_fragment_limit_schema,
    serialize_ft_billing_remove_emails,
    serialize_ft_billing_yearly_totals,
)
from app.dao.date_util import (
    get_financial_year,
    get_financial_year_start,
    get_financial_year_for_datetime
)

platform_stats_blueprint = Blueprint('platform_stats', __name__)

register_errors(platform_stats_blueprint)


def validate_date_range_is_within_a_financial_year(start_date, end_date):
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise InvalidRequest(message="Input must be a date in the format: YYYY-MM-DD", status_code=400)
    if end_date < start_date:
        raise InvalidRequest(message="Start date must be before end date", status_code=400)

    start_fy = get_financial_year_for_datetime(start_date)
    end_fy = get_financial_year_for_datetime(end_date)

    if start_fy != end_fy:
        raise InvalidRequest(message="Date must be in a single financial year.", status_code=400)

    return start_date, end_date


@platform_stats_blueprint.route('')
def get_platform_stats():
    if request.args:
        validate(request.args, platform_stats_request)

    include_from_test_key = request.args.get('include_from_test_key', 'True') != 'False'

    # If start and end date are not set, we are expecting today's stats.
    today = str(convert_utc_to_aet(datetime.utcnow()).date())

    start_date = datetime.strptime(request.args.get('start_date', today), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.args.get('end_date', today), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.args.get('end_date', today), '%Y-%m-%d').date()
    data = fetch_aggregate_stats_by_date_range_for_all_services(
        start_date=start_date,
        end_date=end_date,
        include_from_test_key=include_from_test_key
    )
    stats = format_admin_stats(data)

    return jsonify(stats)


@platform_stats_blueprint.route('/usage-for-all-services')
def get_usage_for_all_services():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start_date, end_date = validate_date_range_is_within_a_financial_year(start_date, end_date)
    sms_costs = fetch_sms_billing_for_all_services(start_date, end_date)

    def present_cost(s):
        return {
            "service_id": str(s.service_id),
            "service_name": s.service_name,
            "sms_rate": float(s.sms_rate),
            # number of free sms available from start of this period FY
            "sms_free_rollover": s.sms_remainder,
            # the total number of units we sent out.
            # fragments * international modifier
            "sms_total_units": int(s.sms_billable_units),
            # number of units sent out after free allowance removed
            "sms_billable_units": int(s.chargeable_billable_sms),
            # total cost of billable units at sms rate
            "sms_cost": float(s.sms_cost),
        }

    service_costs = [present_cost(c) for c in sms_costs]
    return jsonify(sorted(service_costs, key=lambda x: x['service_name']))

