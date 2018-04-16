import pytest

from notifications_utils.clients import DeskproClient, DeskproError


@pytest.fixture(scope='function')
def deskpro_client(app, rmock):
    client = DeskproClient()

    app.config['DESKPRO_API_KEY'] = 'testkey'
    app.config['DESKPRO_API_HOST'] = 'http://deskpro'

    app.config['DESKPRO_DEPT_ID'] = 'department-id'
    app.config['DESKPRO_ASSIGNED_AGENT_TEAM_ID'] = 'agent-id'
    app.config['DESKPRO_PERSON_EMAIL'] = 'donotreply@example.com'

    client.init_app(app)

    return client


def test_create_ticket(deskpro_client, rmock):
    rmock.request("POST", "/api/tickets", status_code=201, json={'status': 'ok'})
    assert deskpro_client.create_ticket('subject', 'message', 'ticket_type') is True

    assert rmock.last_request.headers['X-DeskPRO-API-Key'] == 'testkey'
    assert sorted(rmock.last_request.text.split('&')) == [
        'agent_team_id=agent-id',
        'department_id=department-id',
        'label=ticket_type',
        'message=message',
        'person_email=donotreply%40example.com',
        'subject=subject',
        'urgency=1'
    ]


def test_create_ticket_without_a_label(deskpro_client, rmock):
    rmock.request("POST", "/api/tickets", status_code=201, json={'status': 'ok'})
    assert deskpro_client.create_ticket('subject', 'message') is True

    assert sorted(rmock.last_request.text.split('&')) == [
        'agent_team_id=agent-id',
        'department_id=department-id',
        'message=message',
        'person_email=donotreply%40example.com',
        'subject=subject',
        'urgency=1'
    ]


def test_create_ticket_with_user_name_and_email(deskpro_client, rmock):
    rmock.request("POST", "/api/tickets", status_code=201, json={'status': 'ok'})
    assert deskpro_client.create_ticket('subject', 'message', user_name='Name', user_email='user@example.com') is True

    assert sorted(rmock.last_request.text.split('&')) == [
        'agent_team_id=agent-id',
        'department_id=department-id',
        'message=message',
        'person_email=user%40example.com',
        'person_name=Name',
        'subject=subject',
        'urgency=1'
    ]


def test_create_ticket_error(deskpro_client, app, rmock, mocker):
    rmock.request("POST", "/api/tickets", status_code=401, json={'error_code': 'invalid_auth'})

    mock_logger = mocker.patch.object(app.logger, 'error')

    with pytest.raises(DeskproError):
        deskpro_client.create_ticket('subject', 'message', 'label')

    mock_logger.assert_called_with(
        "Deskpro create ticket request failed with {} '{}'".format(
            401, {'error_code': 'invalid_auth'})
    )
