from unittest.mock import Mock

import pytest
from datetime import datetime, timedelta
from notifications_utils.clients.statsd.statsd_client import StatsdClient


@pytest.fixture(scope='function')
def enabled_statsd_client(app, mocker):
    app.config['STATSD_ENABLED'] = True
    return build_statsd_client(app, mocker)


@pytest.fixture(scope='function')
def disabled_statsd_client(app, mocker):
    app.config['STATSD_ENABLED'] = False
    return build_statsd_client(app, mocker)


def build_statsd_client(app, mocker):
    client = StatsdClient()
    app.config['NOTIFY_ENVIRONMENT'] = "test"
    app.config['NOTIFY_APP_NAME'] = "api"
    app.config['STATSD_HOST'] = "localhost"
    app.config['STATSD_PORT'] = "8000"
    app.config['STATSD_PREFIX'] = "prefix"
    client.init_app(app)
    if not app.config['STATSD_ENABLED']:
        # statsd_client not initialised if statsd not enabled, so lets mock it
        client.statsd_client = Mock()
    mocker.patch.object(client.statsd_client, "incr")
    mocker.patch.object(client.statsd_client, "gauge")
    mocker.patch.object(client.statsd_client, "timing")
    return client


def test_should_create_correctly_formatted_namespace(enabled_statsd_client):
    assert enabled_statsd_client.format_stat_name("test") == "test.notifications.api.test"


def test_should_not_call_incr_if_not_enabled(disabled_statsd_client):
    disabled_statsd_client.incr('key')
    disabled_statsd_client.statsd_client.incr.assert_not_called()


def test_should_call_incr_if_enabled(enabled_statsd_client):
    enabled_statsd_client.incr('key')
    enabled_statsd_client.statsd_client.incr.assert_called_with('test.notifications.api.key', 1, 1)


def test_should_call_incr_with_params_if_enabled(enabled_statsd_client):
    enabled_statsd_client.incr('key', 10, 11)
    enabled_statsd_client.statsd_client.incr.assert_called_with('test.notifications.api.key', 10, 11)


def test_should_not_call_timing_if_not_enabled(disabled_statsd_client):
    disabled_statsd_client.timing('key', 1000)
    disabled_statsd_client.statsd_client.timing.assert_not_called()


def test_should_call_timing_if_enabled(enabled_statsd_client):
    enabled_statsd_client.timing('key', 1000)
    enabled_statsd_client.statsd_client.timing.assert_called_with('test.notifications.api.key', 1000, 1)


def test_should_call_timing_with_params_if_enabled(enabled_statsd_client):
    enabled_statsd_client.timing('key', 1000, 99)
    enabled_statsd_client.statsd_client.timing.assert_called_with('test.notifications.api.key', 1000, 99)


def test_should_not_call_timing_from_dates_method_if_not_enabled(disabled_statsd_client):
    disabled_statsd_client.timing_with_dates('key', datetime.utcnow(), datetime.utcnow())
    disabled_statsd_client.statsd_client.timing.assert_not_called()


def test_should_call_timing_from_dates_method_if_enabled(enabled_statsd_client):
    now = datetime.utcnow()
    enabled_statsd_client.timing_with_dates('key', now + timedelta(seconds=3), now)
    enabled_statsd_client.statsd_client.timing.assert_called_with('test.notifications.api.key', 3, 1)


def test_should_call_timing_from_dates_method_with_params_if_enabled(enabled_statsd_client):
    now = datetime.utcnow()
    enabled_statsd_client.timing_with_dates('key', now + timedelta(seconds=3), now, 99)
    enabled_statsd_client.statsd_client.timing.assert_called_with('test.notifications.api.key', 3, 99)


def test_should_not_call_gauge_if_not_enabled(disabled_statsd_client):
    disabled_statsd_client.gauge('key', 10)
    disabled_statsd_client.statsd_client.gauge.assert_not_called()


def test_should_call_gauge_if_enabled(enabled_statsd_client):
    enabled_statsd_client.gauge('key', 100)
    enabled_statsd_client.statsd_client.gauge.assert_called_with('test.notifications.api.key', 100)
