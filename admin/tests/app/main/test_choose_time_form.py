from freezegun import freeze_time

from app.main.forms import ChooseTimeForm


# Wed Jan 22 2020 09:54:00 GMT+1100 (Australian Eastern Daylight Time)
@freeze_time("2020-01-21T22:54:00.061258Z")
def test_form_contains_later_today_values(app_):
    choices = ChooseTimeForm().scheduled_for.choices

    assert choices[0] == ('', 'Now')
    assert choices[1] == ('2020-01-21T23:00:00.061258', 'Today at 10am')
    assert choices[2] == ('2020-01-22T00:00:00.061258', 'Today at 11am')
    assert choices[3] == ('2020-01-22T01:00:00.061258', 'Today at midday')


# Fri Jan 01 2016 11:09:00 GMT+1100 (Australian Eastern Daylight Time)
@freeze_time("2016-01-01 00:09:00.061258")
def test_form_contains_next_24h(app_):
    choices = ChooseTimeForm().scheduled_for.choices

    assert len(choices) == (
        1 +       # "Now"
        (4 * 24)  # 4 days
    )

    # Friday
    assert choices[0] == ('', 'Now')
    assert choices[1] == ('2016-01-01T01:00:00.061258', 'Today at midday')
    assert choices[2] == ('2016-01-01T02:00:00.061258', 'Today at 1pm')
    assert choices[13] == ('2016-01-01T13:00:00.061258', 'Today at midnight')

    # Saturday
    assert choices[14] == ('2016-01-01T14:00:00.061258', 'Tomorrow at 1am')
    assert choices[37] == ('2016-01-02T13:00:00.061258', 'Tomorrow at midnight')

    # Sunday
    assert choices[38] == ('2016-01-02T14:00:00.061258', 'Sunday at 1am')
    assert choices[61] == ('2016-01-03T13:00:00.061258', 'Sunday at midnight')

    # Monday
    assert choices[62] == ('2016-01-03T14:00:00.061258', 'Monday at 1am')
    assert choices[84] == ('2016-01-04T12:00:00.061258', 'Monday at 11pm')
    assert choices[85] == ('2016-01-04T13:00:00.061258', 'Monday at midnight')


@freeze_time("2016-01-01 11:09:00.061258")
def test_form_defaults_to_now(app_):
    assert ChooseTimeForm().scheduled_for.data == ''


@freeze_time("2016-01-01 11:09:00.061258")
def test_form_contains_next_three_days(app_):
    assert ChooseTimeForm().scheduled_for.categories == [
        'Later today', 'Tomorrow', 'Sunday', 'Monday'
    ]
