import dateutil
import pytz


def utc_string_to_aware_gmt_datetime(date):
    date = dateutil.parser.parse(date)
    forced_utc = date.replace(tzinfo=pytz.utc)
    return forced_utc.astimezone(pytz.timezone('Europe/London'))
