import json
import pytest
from urllib3_mock import Responses
import saplivelink365

from app import sap_sms_client
from app.clients.sms.sap import get_sap_responses


responses = Responses()


def make_auth_response():
    return {
        "access_token": "access_token"
    }


def make_send_sms_response():
    return {
        "livelinkOrderIds": [
            {
                "destination": [
                    "123...789"
                ],
                "livelinkOrderId": [
                    "123456789",
                    "123456777"
                ]
            },
            {
                "destination": [
                    "456...789"
                ],
                "livelinkOrderId": [
                    "1453217689",
                    "153256777"
                ]
            }
        ]
    }


def test_should_return_correct_details_for_sending():
    get_sap_responses('SENT') == 'sending'


@pytest.mark.parametrize('status', ['DELIVERED', 'RECEIVED'])
def test_should_return_correct_details_for_delivered(status):
    get_sap_responses(status) == 'delivered'


def test_should_return_correct_details_for_error():
    get_sap_responses('ERROR') == 'permanent-failure'


def test_should_raise_if_unrecognised_status_code():
    with pytest.raises(KeyError) as e:
        get_sap_responses('unknown_status')
    assert 'unknown_status' in str(e.value)


@responses.activate
def test_send_sms_calls_sap_correctly(notify_db_session, notify_api, mocker):
    to = '+61412345678'
    content = 'my message'
    reference = 'my reference'

    responses.add('POST', '/api/oauth/token',
                  body=json.dumps(make_auth_response()),
                  status=200,
                  content_type='application/json',
                  )
    responses.add('POST', '/api/v2/sms',
                  body=json.dumps(make_send_sms_response()),
                  status=200,
                  content_type='application/json',
                  )

    sap_sms_client.send_sms(to, content, reference)

    assert len(responses.calls) == 2

    req1 = responses.calls[0].request
    assert req1.scheme == 'https'
    assert req1.host == 'livelink.sapmobileservices.com'
    assert req1.url == '/api/oauth/token'
    assert req1.method == 'POST'

    req2 = responses.calls[1].request
    assert req2.scheme == 'https'
    assert req2.host == 'livelink.sapmobileservices.com'
    assert req2.url == '/api/v2/sms'
    assert req2.method == 'POST'

    resp2 = json.loads(responses.calls[1].response.data)
    assert len(resp2['livelinkOrderIds']) == 2


@responses.activate
def test_send_sms_raises_if_sap_errors(notify_db_session, notify_api, mocker):
    to = '+61412345678'
    content = 'my message'
    reference = 'my reference'

    responses.add('POST', '/api/oauth/token',
                  body=json.dumps(make_auth_response()),
                  status=200,
                  content_type='application/json',
                  )
    responses.add('POST', '/api/v2/sms',
                  body='not JSON',
                  status=500,
                  content_type='text/html',
                  )

    with pytest.raises(saplivelink365.exceptions.ApiException):
        sap_sms_client.send_sms(to, content, reference)
