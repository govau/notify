from datetime import datetime, timedelta

import pytz

from app.utils import convert_aest_to_utc


def get_months_for_financial_year(year):
    return [
        convert_aest_to_utc(month) for month in (
            get_months_for_year(7, 13, year) +
            get_months_for_year(1, 7, year + 1)
        )
        if month < datetime.now()
    ]


def get_months_for_year(start, end, year):
    return [datetime(year, month, 1) for month in range(start, end)]


def get_financial_year(year):
    return get_financial_year_start(year), get_financial_year_start(year + 1) - timedelta(microseconds=1)


def get_financial_year_start(year):
    """
     This function converts the start of the financial year "1 July, 00:00 AEST"
     to UTC. The tzinfo is lastly removed from the datetime because the database
     stores the timestamps without timezone.
     :param year: the year for which to calculate the 1 July, 00:00 AEST
     :return: the datetime of 1 July for the given year, for example 2016 = 2016-06-30 14:00:00
    """
    return pytz.timezone('Australia/Sydney').localize(datetime(year, 7, 1, 0, 0, 0)).astimezone(pytz.UTC).replace(
        tzinfo=None)


def get_month_start_and_end_date_in_utc(month_year):
    """
     This function returns the start and end date of the month_year as UTC,
     :param month_year: the datetime to calculate the start and end date for that month
     :return: start_date, end_date, month
    """
    import calendar
    _, num_days = calendar.monthrange(month_year.year, month_year.month)
    first_day = datetime(month_year.year, month_year.month, 1, 0, 0, 0)
    last_day = datetime(month_year.year, month_year.month, num_days, 23, 59, 59, 999999)
    return convert_aest_to_utc(first_day), convert_aest_to_utc(last_day)


def get_current_financial_year_start_year():
    now = datetime.now()
    financial_year_start = now.year
    start_date, end_date = get_financial_year(now.year)
    if now < start_date:
        financial_year_start = financial_year_start - 1
    return financial_year_start
