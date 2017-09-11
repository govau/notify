import pytz

from datetime import datetime, timedelta
from collections import namedtuple

from notifications_utils.timezones import utc_string_to_aware_gmt_datetime


def set_gmt_hour(day, hour):
    return day.astimezone(pytz.timezone('Europe/London')).replace(hour=hour, minute=0)


def get_letter_timings(upload_time):

    LetterTimings = namedtuple(
        'LetterTimings',
        'printed_by, is_printed, earliest_delivery, latest_delivery'
    )

    # shift anything after 5pm to the next day
    processing_day = utc_string_to_aware_gmt_datetime(upload_time) + timedelta(hours=(7))

    print_day, earliest_delivery, latest_delivery = (
        processing_day + timedelta(days=days)
        for days in {
            'Wednesday': (1, 3, 5),
            'Thursday': (1, 4, 5),
            'Friday': (3, 5, 6),
            'Saturday': (2, 4, 5),
        }.get(processing_day.strftime('%A'), (1, 3, 4))
    )

    printed_by = set_gmt_hour(print_day, hour=15)
    now = datetime.utcnow().replace(tzinfo=pytz.timezone('Europe/London'))

    return LetterTimings(
        printed_by=printed_by,
        is_printed=(now > printed_by),
        earliest_delivery=set_gmt_hour(earliest_delivery, hour=16),
        latest_delivery=set_gmt_hour(latest_delivery, hour=16),
    )
