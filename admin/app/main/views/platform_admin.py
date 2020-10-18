import itertools
import collections
from datetime import datetime

from flask import render_template, request, url_for
from flask_login import login_required

from app import (
    billing_api_client,
    complaint_api_client,
    format_date_numeric,
    platform_stats_api_client,
    service_api_client,
    callback_failures_client,
)
from app.main import main
from app.main.forms import DateFilterForm
from app.statistics_utils import (
    get_formatted_percentage,
    get_formatted_percentage_two_dp,
)
from app.utils import (
    Spreadsheet,
    get_page_from_request,
    user_is_platform_admin,
    generate_next_dict,
    generate_previous_dict,
)

COMPLAINT_THRESHOLD = 0.02
FAILURE_THRESHOLD = 3
ZERO_FAILURE_THRESHOLD = 0


@main.route("/platform-admin")
@login_required
@user_is_platform_admin
def platform_admin():
    form = DateFilterForm(request.args)
    api_args = {'detailed': True,
                'only_active': False,     # specifically DO get inactive services
                'include_from_test_key': form.include_from_test_key.data,
                }

    if form.start_date.data:
        api_args['start_date'] = form.start_date.data
        api_args['end_date'] = form.end_date.data or datetime.utcnow().date()

    platform_stats = platform_stats_api_client.get_aggregate_platform_stats(api_args)
    number_of_complaints = complaint_api_client.get_complaint_count(api_args)

    callback_stats = callback_failures_client.get_failing_callback_stats()

    return render_template(
        'views/platform-admin/index.html',
        include_from_test_key=form.include_from_test_key.data,
        form=form,
        global_stats=make_columns(platform_stats, number_of_complaints, callback_stats)
    )


def is_over_threshold(number, total, threshold):
    percentage = number / total * 100 if total else 0
    return percentage > threshold


def get_status_box_data(stats, key, label, threshold=FAILURE_THRESHOLD):
    return {
        'number': "{:,}".format(stats['failures'][key]),
        'label': label,
        'failing': is_over_threshold(
            stats['failures'][key],
            stats['total'],
            threshold
        ),
        'percentage': get_formatted_percentage(stats['failures'][key], stats['total'])
    }


def get_tech_failure_status_box_data(stats):
    stats = get_status_box_data(stats, 'technical-failure', 'technical failures', ZERO_FAILURE_THRESHOLD)
    stats.pop('percentage')
    return stats


def make_columns(global_stats, complaints_number, callback_stats):
    return [
        # email
        {
            'black_box': {
                'number': global_stats['email']['total'],
                'notification_type': 'email'
            },
            'other_data': [
                get_tech_failure_status_box_data(global_stats['email']),
                get_status_box_data(global_stats['email'], 'permanent-failure', 'permanent failures'),
                get_status_box_data(global_stats['email'], 'temporary-failure', 'temporary failures'),
                {
                    'number': complaints_number,
                    'label': 'complaints',
                    'failing': is_over_threshold(complaints_number,
                                                 global_stats['email']['total'], COMPLAINT_THRESHOLD),
                    'percentage': get_formatted_percentage_two_dp(complaints_number, global_stats['email']['total']),
                    'url': url_for('main.platform_admin_list_complaints')
                }
            ],
            'test_data': {
                'number': global_stats['email']['test-key'],
                'label': 'test emails'
            }
        },
        # sms
        {
            'black_box': {
                'number': global_stats['sms']['total'],
                'notification_type': 'sms'
            },
            'other_data': [
                get_tech_failure_status_box_data(global_stats['sms']),
                get_status_box_data(global_stats['sms'], 'permanent-failure', 'permanent failures'),
                get_status_box_data(global_stats['sms'], 'temporary-failure', 'temporary failures'),
                {
                    'number': callback_stats.get('total_failure_count'),
                    'label': 'callback failures',
                    'url': url_for('main.platform_admin_callback_failure_summary')
                },
            ],
            'test_data': {
                'number': global_stats['sms']['test-key'],
                'label': 'test text messages'
            }
        },
    ]


@main.route("/platform-admin/live-services", endpoint='live_services')
@main.route("/platform-admin/trial-services", endpoint='trial_services')
@login_required
@user_is_platform_admin
def platform_admin_services():
    form = DateFilterForm(request.args)
    api_args = {'detailed': True,
                'only_active': False,    # specifically DO get inactive services
                'include_from_test_key': form.include_from_test_key.data,
                }

    if form.start_date.data:
        api_args['start_date'] = form.start_date.data
        api_args['end_date'] = form.end_date.data or datetime.utcnow().date()

    services = filter_and_sort_services(
        service_api_client.get_services(api_args)['data'],
        trial_mode_services=request.endpoint == 'main.trial_services',
    )

    return render_template(
        'views/platform-admin/services.html',
        include_from_test_key=form.include_from_test_key.data,
        form=form,
        services=list(format_stats_by_service(services)),
        page_title='{} services'.format(
            'Trial mode' if request.endpoint == 'main.trial_services' else 'Live'
        ),
        global_stats=create_global_stats(services),
    )


def generate_year_quarters(year):
    yield (f'{year}/Q1', (f'{year}-07-01', f'{year}-09-30'))
    yield (f'{year}/Q2', (f'{year}-10-01', f'{year}-12-31'))
    yield (f'{year}/Q3', (f'{year+1}-01-01', f'{year+1}-03-31'))
    yield (f'{year}/Q4', (f'{year+1}-04-01', f'{year+1}-06-30'))


SUPPORTED_YEARS = [2018, 2019, 2020, 2021, 2022]
SUPPORTED_YEAR_QUARTERS = collections.OrderedDict(
    itertools.chain.from_iterable(
        generate_year_quarters(year) for year in SUPPORTED_YEARS
    )
)

@main.route("/platform-admin/reports")
@login_required
@user_is_platform_admin
def platform_admin_reports():
    return render_template(
        'views/platform-admin/reports.html',
        supported_year_quarters=SUPPORTED_YEAR_QUARTERS,
    )


@main.route("/platform-admin/reports/quarterly-billing.csv")
@login_required
@user_is_platform_admin
def platform_admin_quarterly_billing_csv():
    year_quarter = request.args.get('year_quarter')
    start_date, end_date = SUPPORTED_YEAR_QUARTERS[year_quarter]

    def present_row(billing_data):
        return [
                billing_data.get('service_id'),
                billing_data.get('service_name'),
                start_date,
                end_date,
                billing_data.get('sms_rate'),
                billing_data.get('total_cost'),
                billing_data.get("notifications_sent"),
                billing_data.get("billable_units"),
                billing_data.get("billable_units_adjusted"),
                billing_data.get("sms_free_rollover"),
                billing_data.get("chargeable_units"),
                billing_data.get("domestic_units"),
                billing_data.get("international_units"),
            ]

    data = platform_stats_api_client.get_billing_for_all_services({
        'start_date': start_date,
        'end_date': end_date
    })

    columns = [
        "Service ID", "Service name", "Start date", "End date",
        "SMS rate", "Total cost",
        "SMS Notifications sent", "Billable units", "Billable units adjusted(international)",
        "SMS free rollover from last quarter", "Chargeable units",
        "Domestic units", "International units",
    ]

    csv_data = [columns, *(present_row(d) for d in data)]
    return Spreadsheet.from_rows(csv_data).as_csv_data, 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': f'inline; filename="quarterly-billing-{year_quarter}.csv"'
    }


@main.route("/platform-admin/reports/quarterly-breakdown.csv")
@login_required
@user_is_platform_admin
def platform_admin_quarterly_breakdown_csv():
    year_quarter = request.args.get('year_quarter')
    start_date, end_date = SUPPORTED_YEAR_QUARTERS[year_quarter]

    def present_row(billing_data):
        return [
                billing_data.get('service_id'),
                billing_data.get('service_name'),
                start_date,
                end_date,
                billing_data.get('notification_type'),
                billing_data.get('rate'),
                billing_data.get('rate_multiplier'),
                billing_data.get('notifications_sent'),
                billing_data.get('billable_units_sent'),
                billing_data.get('total_billable_units'),
            ]

    data = platform_stats_api_client.get_usage_for_all_services({
        'start_date': start_date,
        'end_date': end_date
    })

    columns = [
        "Service ID", "Service name", "Start date", "End date",
        "Notification type", "Rate", "Rate multiplier",
        "Notifications sent", "Billable units sent", "Total billable units"
    ]

    csv_data = [columns, *(present_row(d) for d in data)]
    return Spreadsheet.from_rows(csv_data).as_csv_data, 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': f'inline; filename="quarterly-usage-{year_quarter}.csv"'
    }


@main.route("/platform-admin/reports/trial-services.csv")
@login_required
@user_is_platform_admin
def trial_services_csv():
    results = service_api_client.get_trial_services_data()["data"]
    trial_services_columns = [
        "Service ID", "Created date", "Organisation", "Organisation type",
        "Domains", "Service name", "SMS sent this year",
        "Emails sent this year", "Letters sent this year"
    ]
    trial_services_data = []
    trial_services_data.append(trial_services_columns)
    for row in results:
        trial_services_data.append([
            row["service_id"],
            datetime.strptime(row["created_date"], '%a, %d %b %Y %X %Z').strftime("%d-%m-%Y"),
            row["organisation_name"],
            row.get("organisation_type", "TODO"),
            ', '.join(row["domains"]),
            row["service_name"],
            row["sms_totals"],
            row["email_totals"],
            row["letter_totals"],
        ])

    return Spreadsheet.from_rows(trial_services_data).as_csv_data, 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'inline; filename="{} trial services report.csv"'.format(
            format_date_numeric(datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
        )
    }


@main.route("/platform-admin/reports/live-services.csv")
@login_required
@user_is_platform_admin
def live_services_csv():
    results = service_api_client.get_live_services_data()["data"]
    live_services_columns = [
        "Service ID", "Organisation", "Organisation type", "Domains", "Service name", "Consent to research", "Main contact",
        "Contact email", "Contact mobile", "Live date", "Created date", "SMS volume intent", "Email volume intent",
        "Letter volume intent", "SMS sent this year", "Emails sent this year", "Letters sent this year"
    ]
    live_services_data = []
    live_services_data.append(live_services_columns)
    for row in results:
        live_services_data.append([
            row["service_id"],
            row["organisation_name"],
            row.get("organisation_type", "TODO"),
            ', '.join(row["domains"]),
            row["service_name"],
            row.get("consent_to_research", "TODO"),
            row["contact_name"],
            row["contact_email"],
            row["contact_mobile"],
            datetime.strptime(
                row["live_date"], '%a, %d %b %Y %X %Z'
            ).strftime("%d-%m-%Y") if row["live_date"] else None,
            datetime.strptime(row["created_date"], '%a, %d %b %Y %X %Z').strftime("%d-%m-%Y"),
            row.get("sms_volume_intent", "TODO"),
            row.get("email_volume_intent", "TODO"),
            row.get("letter_volume_intent", "TODO"),
            row["sms_totals"],
            row["email_totals"],
            row["letter_totals"],
        ])

    return Spreadsheet.from_rows(live_services_data).as_csv_data, 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'inline; filename="{} live services report.csv"'.format(
            format_date_numeric(datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
        )
    }


@main.route("/platform-admin/complaints")
@login_required
@user_is_platform_admin
def platform_admin_list_complaints():
    page = get_page_from_request()
    if page is None:
        abort(404, "Invalid page argument ({}).".format(request.args.get('page')))

    response = complaint_api_client.get_all_complaints(page=page)

    prev_page = None
    if response['links'].get('prev'):
        prev_page = generate_previous_dict('main.platform_admin_list_complaints', None, page)
    next_page = None
    if response['links'].get('next'):
        next_page = generate_next_dict('main.platform_admin_list_complaints', None, page)

    return render_template(
        'views/platform-admin/complaints.html',
        complaints=response['complaints'],
        page_title='All Complaints',
        page=page,
        prev_page=prev_page,
        next_page=next_page,
    )


@main.route("/platform-admin/callback-failures")
@login_required
@user_is_platform_admin
def platform_admin_callback_failures():
    page = get_page_from_request()
    if page is None:
        abort(404, "Invalid page argument ({}).".format(request.args.get('page')))

    response = callback_failures_client.get_failing_callbacks(page=page)

    prev_page = None
    if response['links'].get('prev'):
        prev_page = generate_previous_dict('main.platform_admin_callback_failures', None, page)
    next_page = None
    if response['links'].get('next'):
        next_page = generate_next_dict('main.platform_admin_callback_failures', None, page)

    return render_template(
        'views/platform-admin/callback_failures.html',
        callback_failures=response['callbacks'],
        page_title='Callback failures',
        page=page,
        prev_page=prev_page,
        next_page=next_page,
    )


@main.route("/platform-admin/callback-failure-summary")
@login_required
@user_is_platform_admin
def platform_admin_callback_failure_summary():
    summary_rows = callback_failures_client.get_failing_callback_summary()

    return render_template(
        'views/platform-admin/callback_failure_summary.html',
        summary_rows=summary_rows,
        page_title='Callback failures over the last 3 days',
    )


def sum_service_usage(service):
    total = 0
    for notification_type in service['statistics'].keys():
        total += service['statistics'][notification_type]['requested']
    return total


def filter_and_sort_services(services, trial_mode_services=False):
    return [
        service for service in sorted(
            services,
            key=lambda service: (
                service['active'],
                sum_service_usage(service),
                service['created_at']
            ),
            reverse=True,
        )
        if service['restricted'] == trial_mode_services
    ]


def create_global_stats(services):
    stats = {
        'email': {
            'delivered': 0,
            'failed': 0,
            'requested': 0
        },
        'sms': {
            'delivered': 0,
            'failed': 0,
            'requested': 0
        },
        'letter': {
            'delivered': 0,
            'failed': 0,
            'requested': 0
        }
    }
    for service in services:
        for msg_type, status in itertools.product(('sms', 'email', 'letter'), ('delivered', 'failed', 'requested')):
            stats[msg_type][status] += service['statistics'][msg_type][status]

    for stat in stats.values():
        stat['failure_rate'] = get_formatted_percentage(stat['failed'], stat['requested'])
    return stats


def format_stats_by_service(services):
    for service in services:
        yield {
            'id': service['id'],
            'name': service['name'],
            'stats': {
                msg_type: {
                    'sending': stats['requested'] - stats['delivered'] - stats['failed'],
                    'delivered': stats['delivered'],
                    'failed': stats['failed'],
                    'templates': stats['templates']
                }
                for msg_type, stats in service['statistics'].items()
            },
            'restricted': service['restricted'],
            'research_mode': service['research_mode'],
            'created_at': service['created_at'],
            'active': service['active'],
            'domains': service['domains'],
            'organisation_type': service['organisation_type']
        }
