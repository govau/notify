import pytest

from notifications_utils.international_billing_rates import INTERNATIONAL_BILLING_RATES


def test_international_billing_rates_exists():
    assert INTERNATIONAL_BILLING_RATES['1']['names'][0] == 'Canada'


@pytest.mark.parametrize('country_prefix, values', INTERNATIONAL_BILLING_RATES.items())
def test_international_billing_rates_are_in_correct_format(country_prefix, values):
    assert isinstance(country_prefix, str)
    # we don't want the prefixes to have + at the beginning for instance
    assert country_prefix.isdigit()

    assert set(values.keys()) == {'attributes', 'billable_units', 'names'}

    assert isinstance(values['billable_units'], int)
    assert 1 <= values['billable_units'] <= 3

    assert isinstance(values['names'], list)
    assert all(isinstance(country, str) for country in values['names'])

    assert isinstance(values['attributes'], dict)
