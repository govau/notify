from datetime import datetime


def daily_limit_cache_key(service_id):
    return "{}-{}-{}".format(str(service_id), datetime.utcnow().strftime("%Y-%m-%d"), "count")


def rate_limit_cache_key(service_id, api_key_type):
    return "{}-{}".format(str(service_id), api_key_type)
