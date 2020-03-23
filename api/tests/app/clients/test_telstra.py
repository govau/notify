import json
from urllib3_mock import Responses

from app import telstra_sms_client
from app.models import (
    NOTIFICATION_PERMANENT_FAILURE,
)


responses = Responses()


def make_auth_response():
    return {
        "access_token": "access_token"
    }


@responses.activate
def test_send_sms_returns_permanent_failure_when_number_not_exists(notify_api):
    to = '+61412345678'
    content = 'test, please ignore'
    reference = '6cdeb27b-761d-41ca-878f-b584294814f2'

    response_dict = {
        "messages": [
            {
                "to": "+61412345678",
                "deliveryStatus": "DeliveryImpossible",
                "messageStatusURL": "https://tapi.telstra.com/v2/messages/sms//status",
                "status": "400",
                "code": "TO-MSISDN-NOT-VALID",
                "message": "Refer to API docs at https://dev.telstra.com",
            },
        ],
        "Country": [],
        "messageType": "SMS",
        "numberSegments": 1,
    }

    responses.add('POST', '/v2/oauth/token',
                  body=json.dumps(make_auth_response()),
                  status=200,
                  content_type='application/json',
                  )
    responses.add('POST', '/v2/messages/sms',
                  body=json.dumps(response_dict),
                  status=400,
                  content_type='application/json',
                  )

    reference, status = telstra_sms_client.send_sms(to, content, reference)

    assert reference is None
    assert status == NOTIFICATION_PERMANENT_FAILURE
