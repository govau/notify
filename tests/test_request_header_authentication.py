from unittest import mock  # noqa

import pytest
from werkzeug.test import EnvironBuilder

from notifications_utils.request_helper import CustomRequest, _check_proxy_header_secret


@pytest.mark.parametrize('test_input,expected', [
    ({'header_name': 'X-Custom-Forwarder', 'header_value': 'right_key', 'secrets': ['right_key', 'old_key']}, (True, 'Key used: 1')),  # noqa
    ({'header_name': 'X-Custom-Forwarder', 'header_value': 'right_key', 'secrets': ['right_key']}, (True, 'Key used: 1')),  # noqa
    ({'header_name': 'X-Custom-Forwarder', 'header_value': 'right_key', 'secrets': ['right_key', '']}, (True, 'Key used: 1')),  # noqa
    ({'header_name': 'My-New-Header', 'header_value': 'right_key', 'secrets': ['right_key', '']}, (True, 'Key used: 1')),  # noqa
    ({'header_name': 'X-Custom-Forwarder', 'header_value': 'right_key', 'secrets': ['', 'right_key']}, (True, 'Key used: 2')),  # noqa
    ({'header_name': 'X-Custom-Forwarder', 'header_value': 'right_key', 'secrets': ['', 'old_key', 'right_key']}, (True, 'Key used: 3')),  # noqa
    ({'secrets': ['old_key', 'right_key']}, (False, 'Header missing')),
    ({'header_name': 'X-Custom-Forwarder', 'header_value': '', 'secrets': ['right_key', 'old_key']}, (False, 'Header exists but is empty')),  # noqa
    ({'header_name': 'X-Custom-Forwarder', 'header_value': 'right_key', 'secrets': ['', None]}, (False, 'Secrets are not configured')),  # noqa
    ({'header_name': 'X-Custom-Forwarder', 'header_value': 'wrong_key', 'secrets': ['right_key', 'old_key']}, (False, "Header didn't match any keys")),  # noqa
])
def test_request_header_authorization(test_input, expected):
    builder = EnvironBuilder()
    if 'header_name' in test_input:
        builder.headers[test_input['header_name']] = test_input['header_value']
    request = CustomRequest(builder.get_environ())

    if test_input.get('header_name'):
        res = _check_proxy_header_secret(request, test_input['secrets'], test_input.get('header_name'))
    else:
        res = _check_proxy_header_secret(request, test_input['secrets'])
    assert res == expected
