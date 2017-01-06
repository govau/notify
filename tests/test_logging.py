import logging as builtin_logging
import uuid
from pathlib import Path

import pytest

from notifications_utils import logging


def test_should_build_complete_log_line():
    service_id = uuid.uuid4()
    extra_fields = {
        'method': "method",
        'url': "url",
        'status': 200,
        'time_taken': "time_taken",
        'service_id': service_id
    }
    assert "{service_id} method url 200 time_taken".format(
        service_id=str(service_id)) == logging.build_log_line(extra_fields)


def test_should_build_complete_log_line_ignoring_missing_fields():
    service_id = uuid.uuid4()
    extra_fields = {
        'method': "method",
        'status': 200,
        'time_taken': "time_taken",
        'service_id': service_id
    }
    assert "{service_id} method 200 time_taken".format(
        service_id=str(service_id)) == logging.build_log_line(extra_fields)


def test_should_build_log_line_without_service_id():
    extra_fields = {
        'method': "method",
        'url': "url",
        'status': 200,
        'time_taken': "time_taken"
    }
    assert "method url 200 time_taken" == logging.build_log_line(extra_fields)


def test_should_build_log_line_without_service_id_or_time_taken():
    extra_fields = {
        'method': "method",
        'url': "url",
        'status': 200
    }
    assert "method url 200" == logging.build_log_line(extra_fields)


def test_should_build_complete_statsd_line():
    service_id = uuid.uuid4()
    extra_fields = {
        'method': "method",
        'endpoint': "endpoint",
        'status': 200,
        'service_id': service_id
    }
    assert "service-id.{service_id}.method.endpoint.200".format(
        service_id=str(service_id)) == logging.build_statsd_line(extra_fields)


def test_should_build_complete_statsd_line_without_service_id_prefix_for_admin_api_calls():
    service_id = uuid.uuid4()
    extra_fields = {
        'method': "method",
        'endpoint': "endpoint",
        'status': 200,
        'service_id': 'notify-admin'
    }
    assert "notify-admin.method.endpoint.200".format(
        service_id=str(service_id)) == logging.build_statsd_line(extra_fields)


def test_should_build_complete_statsd_line_ignoring_missing_fields():
    service_id = uuid.uuid4()
    extra_fields = {
        'method': "method",
        'endpoint': "endpoint",
        'service_id': service_id
    }
    assert "service-id.{service_id}.method.endpoint".format(
        service_id=str(service_id)) == logging.build_statsd_line(extra_fields)


def test_should_build_statsd_line_without_service_id_or_time_taken():
    extra_fields = {
        'method': "method",
        'endpoint': "endpoint",
        'status': 200
    }
    assert "method.endpoint.200" == logging.build_statsd_line(extra_fields)


@pytest.mark.parametrize('debug_mode, cloudfoundry, formatter', [
    (True, True, logging.CustomLogFormatter),
    (True, False, logging.CustomLogFormatter),
    (False, True, logging.JSONFormatter),
    # false false is tested separately
])
def test_get_handlers_sets_up_logging_appropriately(debug_mode, cloudfoundry, formatter):
    class App:
        config = {
            'NOTIFY_LOG_PATH': 'foo',
            'NOTIFY_APP_NAME': 'bar',
            'NOTIFY_LOG_LEVEL': 'ERROR',
            'CLOUDFOUNDRY': cloudfoundry
        }
        debug = debug_mode

    app = App()

    handlers = logging.get_handlers(app)

    assert len(handlers) == 1
    assert type(handlers[0]) == builtin_logging.StreamHandler
    assert type(handlers[0].formatter) == formatter


def test_get_handlers_sets_up_logging_appropriately_on_live(tmpdir):
    class App:
        config = {
            # make a tempfile called foo
            'NOTIFY_LOG_PATH': str(tmpdir / 'foo'),
            'NOTIFY_APP_NAME': 'bar',
            'NOTIFY_LOG_LEVEL': 'ERROR',
            'CLOUDFOUNDRY': False
        }
        debug = False

    app = App()

    handlers = logging.get_handlers(app)

    assert len(handlers) == 2
    assert type(handlers[0]) == builtin_logging.FileHandler
    assert type(handlers[0].formatter) == logging.CustomLogFormatter

    assert type(handlers[1]) == builtin_logging.FileHandler
    assert type(handlers[1].formatter) == logging.JSONFormatter

    assert (tmpdir / 'foo').isfile()
    assert (tmpdir / 'foo.json').isfile()
