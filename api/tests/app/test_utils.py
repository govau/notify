from datetime import datetime
import pytz
import pytest

from app.utils import (
    get_sydney_midnight_in_utc,
    get_midnight_for_day_before,
    convert_utc_to_local,
    convert_utc_to_aet,
    convert_local_to_utc,
    convert_aet_to_utc)

@pytest.mark.parametrize('date, expected_date', [
    (datetime(2016, 7, 26, 00, 30), datetime(2016, 7, 25, 14, 00)),  # 2016-07-26 is outside daylight savings time
    (datetime(2016, 6, 26, 00, 00), datetime(2016, 6, 25, 14, 00)),  # 2016-06-26 is outside daylight savings time
    (datetime(2016, 11, 26, 00, 00), datetime(2016, 11, 25, 13, 00)),  # 2016-11-26 is during daylight savings time
    (datetime(2016, 11, 26, 11, 59), datetime(2016, 11, 25, 13, 00)),  # 2016-11-26 is during daylight savings time
    (datetime(2016, 11, 26, 23, 59), datetime(2016, 11, 25, 13, 00)),  # 2016-11-26 is during daylight savings time
])
def test_get_sydney_midnight_in_utc_returns_expected_date(date, expected_date):
    """
     :param date a localized datetime
     :param expected_date a UTC datetime
    """
    assert get_sydney_midnight_in_utc(date) == expected_date


@pytest.mark.parametrize('date, expected_date', [
    (datetime(2016, 7, 26, 0, 30), datetime(2016, 7, 24, 14, 0)),
    (datetime(2016, 6, 26, 0, 0), datetime(2016, 6, 24, 14, 0)),
    (datetime(2016, 11, 26, 11, 59), datetime(2016, 11, 24, 13, 0)),
])
def test_get_midnight_for_day_before_returns_expected_date(date, expected_date):
    assert get_midnight_for_day_before(date) == expected_date


@pytest.mark.parametrize('date, local_tz, expected_date', [
    (datetime(2017, 3, 26, 23, 0), 'Europe/London', datetime(2017, 3, 27, 0, 0)),    # 2017 BST switchover
    (datetime(2017, 3, 20, 23, 0), 'Europe/London',datetime(2017, 3, 20, 23, 0)),
    (datetime(2017, 3, 28, 10, 0), 'Europe/London',datetime(2017, 3, 28, 11, 0)),
    (datetime(2017, 10, 28, 1, 0), 'Europe/London',datetime(2017, 10, 28, 2, 0)),
    (datetime(2017, 10, 29, 1, 0), 'Europe/London',datetime(2017, 10, 29, 1, 0)),
    (datetime(2017, 5, 12, 14), 'Europe/London',datetime(2017, 5, 12, 15, 0)),

    (datetime(2016, 3, 30, 14, 0), 'Australia/Sydney', datetime(2016, 3, 31, 1, 0)),  # During AEDT
    (datetime(2017, 3, 26, 23, 0), 'Australia/Sydney',datetime(2017, 3, 27, 10, 0)),
    (datetime(2017, 3, 20, 23, 0), 'Australia/Sydney',datetime(2017, 3, 21, 10, 0)),
    (datetime(2017, 3, 28, 10, 0), 'Australia/Sydney',datetime(2017, 3, 28, 21, 0)),
    (datetime(2017, 4, 2, 3, 0), 'Australia/Sydney',datetime(2017, 4, 2, 13, 0)),  # AEDT crossover
    (datetime(2017, 10, 1, 2, 0), 'Australia/Sydney',datetime(2017, 10, 1, 13, 0)),  # AEDT crossover
    (datetime(2017, 10, 28, 1, 0), 'Australia/Sydney',datetime(2017, 10, 28, 12, 0)),
    (datetime(2017, 10, 29, 1, 0), 'Australia/Sydney',datetime(2017, 10, 29, 12, 0)),
    (datetime(2017, 5, 12, 14), 'Australia/Sydney',datetime(2017, 5, 13, 0, 0)),
])
def test_get_utc_in_local_returns_expected_date(date, local_tz, expected_date):
    assert convert_utc_to_local(date, pytz.timezone(local_tz)) == expected_date


@pytest.mark.parametrize('date, expected_date', [
    (datetime(2016, 3, 30, 14, 0), datetime(2016, 3, 31, 1, 0)),  # During AEDT
    (datetime(2017, 3, 26, 23, 0), datetime(2017, 3, 27, 10, 0)),
    (datetime(2017, 3, 20, 23, 0), datetime(2017, 3, 21, 10, 0)),
    (datetime(2017, 3, 28, 10, 0), datetime(2017, 3, 28, 21, 0)),
    (datetime(2017, 4, 2, 3, 0), datetime(2017, 4, 2, 13, 0)),  # AEDT crossover
    (datetime(2017, 10, 1, 2, 0), datetime(2017, 10, 1, 13, 0)),  # AEDT crossover
    (datetime(2017, 10, 28, 1, 0), datetime(2017, 10, 28, 12, 0)),
    (datetime(2017, 10, 29, 1, 0), datetime(2017, 10, 29, 12, 0)),
    (datetime(2017, 5, 12, 14), datetime(2017, 5, 13, 0, 0)),
])
def test_get_utc_in_aet_returns_expected_date(date, expected_date):
    assert convert_utc_to_aet(date) == expected_date


@pytest.mark.parametrize('date, local_tz, expected_date', [
    ("2017-05-12 13:15", "Europe/London", datetime(2017, 5, 12, 12, 15)),
    ("2017-12-12 13:15", "Europe/London", datetime(2017, 12, 12, 13, 15)),

    ("2017-05-12 13:15", "Australia/Sydney", datetime(2017, 5, 12, 3, 15)),
])
def test_convert_local_to_utc(date, local_tz, expected_date):
    dt = datetime.strptime(date, "%Y-%m-%d %H:%M")
    assert convert_local_to_utc(dt, pytz.timezone(local_tz)) == expected_date


def test_convert_aet_to_utc():
    aet = "2017-05-12 13:15"
    aet_datetime = datetime.strptime(aet, "%Y-%m-%d %H:%M")
    utc = convert_aet_to_utc(aet_datetime)
    assert utc == datetime(2017, 5, 12, 3, 15)
