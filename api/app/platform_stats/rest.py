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
