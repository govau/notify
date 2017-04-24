

def test_international_billing_rates_exists():
    from notifications_utils.international_billing_rates import INTERNATIONAL_BILLING_RATES
    assert INTERNATIONAL_BILLING_RATES['1']['names'][0] == 'Canada'
