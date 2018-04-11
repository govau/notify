from unittest.mock import ANY, Mock
from notifications_utils.statsd_decorators import statsd


class AnyStringWith(str):
    def __eq__(self, other):
        return self in other


def test_should_call_statsd(app, mocker):
    app.config['NOTIFY_ENVIRONMENT'] = "test"
    app.config['NOTIFY_APP_NAME'] = "api"
    app.config['STATSD_HOST'] = "localhost"
    app.config['STATSD_PORT'] = "8000"
    app.config['STATSD_PREFIX'] = "prefix"
    app.statsd_client = Mock()

    mock_logger = mocker.patch.object(app.logger, 'debug')

    @statsd(namespace="test")
    def test_function():
        return True

    assert test_function()
    mock_logger.assert_called_once_with(AnyStringWith("test call test_function took "))
    app.statsd_client.incr.assert_called_once_with("test.test_function")
    app.statsd_client.timing.assert_called_once_with("test.test_function", ANY)
