import pytest

from notifications_utils.timezones import utc_string_to_aware_gmt_datetime


@pytest.mark.parametrize('input_value', [
    'foo',
    100,
    True,
    False,
    None,
])
def test_utc_string_to_aware_gmt_datetime_rejects_bad_input(input_value):
    with pytest.raises(Exception):
        utc_string_to_aware_gmt_datetime(input_value)


@pytest.mark.parametrize('naive_time, expected_aware_hour', [
    ('2000-12-1 20:01', '20:01'),
    ('2000-06-1 20:01', '21:01'),
])
def test_utc_string_to_aware_gmt_datetime_handles_summer_and_winter(
    naive_time,
    expected_aware_hour,
):
    assert utc_string_to_aware_gmt_datetime(naive_time).strftime('%H:%M') == expected_aware_hour
