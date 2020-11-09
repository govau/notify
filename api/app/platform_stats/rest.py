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
from app.dao.fact_billing_dao import fetch_billing_for_all_services

platform_stats_blueprint = Blueprint('platform_stats', __name__)

register_errors(platform_stats_blueprint)


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


@platform_stats_blueprint.route('/services-billing')
def get_all_services_billing():
    billing_data = fetch_billing_for_all_services()

    def present_data(s):
        return {
            "service_id": str(s.service_id),
            "service_name": s.service_name,

            "breakdown_aet": str(s.breakdown_aet),
            "breakdown_fy": str(s.breakdown_fy),
            "breakdown_fy_year": int(s.breakdown_fy_year),
            "breakdown_fy_quarter": int(s.breakdown_fy_quarter),

            "notifications": int(s.notifications),
            "notifications_sms": int(s.notifications_sms or 0),
            "notifications_email": int(s.notifications_email or 0),

            "fragments_free_limit": int(s.fragments_free_limit),
            "fragments_domestic": int(s.fragments_domestic),
            "fragments_international": int(s.fragments_international),

            "cost": float(s.cost),
            "cost_chargeable": float(s.cost_chargeable),
            "cost_cumulative": float(s.cost_cumulative),
            "cost_chargeable_cumulative": float(s.cost_chargeable_cumulative),

            "units": float(s.units),
            "units_cumulative": float(s.units_cumulative),
            "units_chargeable": float(s.units_chargeable),
            "units_chargeable_cumulative": float(s.units_chargeable_cumulative),
            "units_free_available": float(s.units_free_available),
            "units_free_remaining": float(s.units_free_remaining),
            "units_free_used": float(s.units_free_used),

            "unit_rate_domestic": float(s.unit_rate_domestic),
            "unit_rate_international": float(s.unit_rate_international),
        }

    return jsonify([present_data(x) for x in billing_data])
