from datetime import datetime

import pytest

from app.dao.date_util import get_financial_year, get_financial_year_start, get_month_start_and_end_date_in_utc


def test_get_financial_year():
    start, end = get_financial_year(2000)
    assert str(start) == '2000-06-30 14:00:00' # 01 July 2000 00:00:00.0 in UTC
    assert str(end) == '2001-06-30 13:59:59.999999' # 30 June 2001 23:59:59.999999 in UTC


def test_get_financial_year_start():
    start = get_financial_year_start(2016)
    assert str(start) == '2016-06-30 14:00:00'
    assert start.tzinfo is None


@pytest.mark.parametrize("month, year, expected_start, expected_end", [
    (7, 2017, datetime(2017, 6, 30, 14, 00, 00), datetime(2017, 7, 31, 13, 59, 59, 999999)), # During AEST
    (2, 2016, datetime(2016, 1, 31, 13, 00, 00), datetime(2016, 2, 29, 12, 59, 59, 999999)), # During ADST
    (2, 2017, datetime(2017, 1, 31, 13, 00, 00), datetime(2017, 2, 28, 12, 59, 59, 999999)), # During ADST
    (9, 2018, datetime(2018, 8, 31, 14, 00, 00), datetime(2018, 9, 30, 13, 59, 59, 999999)), # During AEST
    (12, 2019, datetime(2019, 11, 30, 13, 00, 00), datetime(2019, 12, 31, 12, 59, 59, 999999)) # During ADST
])
def test_get_month_start_and_end_date_in_utc(month, year, expected_start, expected_end):
    month_year = datetime(year, month, 10, 13, 30, 00)
    result = get_month_start_and_end_date_in_utc(month_year)
    assert result[0] == expected_start
    assert result[1] == expected_end
