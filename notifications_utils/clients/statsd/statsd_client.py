from statsd import StatsClient


class StatsdClient():
    def __init__(self):
        self.statsd_client = None

    def init_app(self, app, *args, **kwargs):
        self.active = app.config.get('STATSD_ENABLED')
        self.namespace = "{}.notifications.{}.".format(
            app.config.get('NOTIFY_ENVIRONMENT'),
            app.config.get('NOTIFY_APP_NAME')
        )

        if self.active:
            self.statsd_client = StatsClient(
                app.config.get('STATSD_HOST'),
                app.config.get('STATSD_PORT'),
                prefix=app.config.get('STATSD_PREFIX')
            )

    def format_stat_name(self, stat):
        return self.namespace + stat

    def incr(self, stat, count=1, rate=1):
        if self.active:
            self.statsd_client.incr(self.format_stat_name(stat), count, rate)

    def gauge(self, stat, count):
        if self.active:
            self.statsd_client.gauge(self.format_stat_name(stat), count)

    def timing(self, stat, delta, rate=1):
        if self.active:
            self.statsd_client.timing(self.format_stat_name(stat), delta, rate)

    def timing_with_dates(self, stat, start, end, rate=1):
        if self.active:
            delta = (start - end).total_seconds()
            self.statsd_client.timing(self.format_stat_name(stat), delta, rate)
