import mock
from werkzeug.test import EnvironBuilder

from notifications_utils import request_id
from notifications_utils.request_id import CustomRequest


def test_get_request_id_from_request_id_header():
    builder = EnvironBuilder()
    builder.headers['NotifyRequestID'] = 'from-header'
    builder.headers['NotifyDownstreamNotifyRequestID'] = 'from-downstream'
    request = CustomRequest(builder.get_environ())

    request_id = request._get_request_id('NotifyRequestID',
                                         'NotifyDownstreamRequestID')

    assert request_id == 'from-header'


def test_get_request_id_from_downstream_header():
    builder = EnvironBuilder()
    builder.headers['NotifyDownstreamRequestID'] = 'from-downstream'
    request = CustomRequest(builder.get_environ())

    request_id = request._get_request_id('NotifyRequestID',
                                         'NotifyDownstreamRequestID')

    assert request_id == 'from-downstream'


@mock.patch('notifications_utils.request_id.uuid.uuid4')
def test_get_request_id_with_no_downstream_header_configured(uuid4_mock):
    builder = EnvironBuilder()
    builder.headers[''] = 'from-downstream'
    request = CustomRequest(builder.get_environ())
    uuid4_mock.return_value = 'generated'

    request_id = request._get_request_id('NotifyRequestID', '')

    uuid4_mock.assert_called_once()
    assert request_id == 'generated'


@mock.patch('notifications_utils.request_id.uuid.uuid4')
def test_get_request_id_generates_id(uuid4_mock):
    builder = EnvironBuilder()
    request = CustomRequest(builder.get_environ())
    uuid4_mock.return_value = 'generated'

    request_id = request._get_request_id('NotifyRequestID',
                                         'NotifyDownstreamRequestID')

    uuid4_mock.assert_called_once()
    assert request_id == 'generated'


def test_request_id_is_set_on_response(app):
    request_id.init_app(app)
    client = app.test_client()

    with app.app_context():
        response = client.get('/', headers={'NotifyRequestID': 'generated'})
        assert response.headers['NotifyRequestID'] == 'generated'.encode('utf-8')


def test_request_id_is_set_on_error_response(app):
    request_id.init_app(app)
    client = app.test_client()

    @app.route('/')
    def error_route():
        raise Exception()

    with app.app_context():
        response = client.get('/', headers={'NotifyRequestID': 'generated'})
        assert response.status_code == 500
        assert response.headers['NotifyRequestID'] == 'generated'.encode('utf-8')
