from app.dao.date_util import get_current_financial_year_start_year
from freezegun import freeze_time


# see get_financial_year for conversion of financial years.
@freeze_time("2017-06-30 13:59:59.999999")
def test_get_current_financial_year_start_year_before_june():
    current_fy = get_current_financial_year_start_year()
    assert current_fy == 2016


@freeze_time("2017-06-30 14:00:00.000000")
def test_get_current_financial_year_start_year_after_july():
    current_fy = get_current_financial_year_start_year()
    assert current_fy == 2017
