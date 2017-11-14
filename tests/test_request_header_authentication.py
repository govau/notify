from unittest import mock  # noqa
from werkzeug.test import EnvironBuilder

from notifications_utils.request_helper import CustomRequest, _check_proxy_header_secret


def test_request_header_contains_correct_secret():
    builder = EnvironBuilder()
    builder.headers['X-Custom-Forwarder'] = '123-456-789'
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['123-456-789', '987-654-321'])
    assert res == (True, "Key used: 1")


def test_request_header_contains_correct_secret_single_key():
    builder = EnvironBuilder()
    builder.headers['X-Custom-Forwarder'] = '123-456-789'
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['123-456-789'])
    assert res == (True, "Key used: 1")


def test_request_header_contains_correct_secret_second_key_empty():
    builder = EnvironBuilder()
    builder.headers['X-Custom-Forwarder'] = '123-456-789'
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['123-456-789', ''])
    assert res == (True, "Key used: 1")


def test_request_header_contains_correct_secret_custom_header_name():
    builder = EnvironBuilder()
    builder.headers['My-Custom-Header'] = '123-456-789'
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['123-456-789', ''], 'My-Custom-Header')
    assert res == (True, "Key used: 1")


def test_request_header_contains_correct_secret_first_key_empty():
    builder = EnvironBuilder()
    builder.headers['X-Custom-Forwarder'] = '123-456-789'
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['', '123-456-789'])
    assert res == (True, "Key used: 2")


def test_request_header_contains_correct_secret_more_than_two_secrets():
    builder = EnvironBuilder()
    builder.headers['X-Custom-Forwarder'] = '123-456-789'
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['', '345-678-910', '123-456-789'])
    assert res == (True, "Key used: 3")


def test_request_header_missing():
    builder = EnvironBuilder()
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['123-456-789', '987-654-321'])
    assert res == (False, "Header missing")


def test_request_header_missing_value():
    builder = EnvironBuilder()
    builder.headers['X-Custom-Forwarder'] = ''
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['123-456-789', '987-654-321'])
    assert res == (False, "Header exists but is empty")


def test_request_header_missing_secrets():
    builder = EnvironBuilder()
    builder.headers['X-Custom-Forwarder'] = '123-456-789'
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['', None])
    assert res == (False, "Secrets are not configured")


def test_request_header_wrong_secret():
    builder = EnvironBuilder()
    builder.headers['X-Custom-Forwarder'] = '133-433-733'
    request = CustomRequest(builder.get_environ())

    res = _check_proxy_header_secret(request, ['123-456-789', '987-654-321'])
    assert res == (False, "Header didn't match any keys")
