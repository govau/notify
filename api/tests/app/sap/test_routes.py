import json
import urllib.parse
import pytest
from requests.auth import _basic_auth_str
from app import db
from app.sap.oauth2 import OAuth2Token


def fetch_token(client, oauth2_client):
    data = {'grant_type': 'client_credentials'}
    headers = [
        ('Authorization', _basic_auth_str(oauth2_client.client_id, oauth2_client.client_secret)),
        ('Content-Type', 'application/x-www-form-urlencoded')
    ]
    response = client.post(
        '/sap/oauth2/token',
        data=urllib.parse.urlencode(data),
        headers=headers,
    )
    return response, json.loads(response.get_data(as_text=True))


def test_issue_token(client, sample_sap_oauth2_client):
    response, token = fetch_token(client, sample_sap_oauth2_client)
    assert response.status_code == 200
    assert token['access_token'] != ""
    assert token['expires_in'] > 0
    assert token['token_type'] == "Bearer"


@pytest.mark.parametrize('grant_type', (
    (''),
    ('invalid'),
))
def test_issue_token_returns_error_with_invalid_grant_type(client, grant_type):
    data = {'grant_type': grant_type}
    headers = [('Content-Type', 'application/x-www-form-urlencoded')]
    response = client.post(
        '/sap/oauth2/token',
        data=urllib.parse.urlencode(data),
        headers=headers,
    )
    assert response.status_code == 400
    assert json.loads(response.get_data(as_text=True))['error'] == 'unsupported_grant_type'


def test_issue_token_returns_error_with_bad_credentials(client, sample_sap_oauth2_client):
    data = {'grant_type': 'client_credentials'}
    headers = [
        ('Authorization', _basic_auth_str('0000', '1111')),
        ('Content-Type', 'application/x-www-form-urlencoded')
    ]
    response = client.post(
        '/sap/oauth2/token',
        data=urllib.parse.urlencode(data),
        headers=headers,
    )
    assert response.status_code == 401
    assert json.loads(response.get_data(as_text=True))['error'] == 'invalid_client'


def test_revoke_token(client, sample_sap_oauth2_client):
    _, token = fetch_token(client, sample_sap_oauth2_client)

    data = {'token': token['access_token']}
    headers = [
        ('Authorization', _basic_auth_str(sample_sap_oauth2_client.client_id, sample_sap_oauth2_client.client_secret)),
        ('Content-Type', 'application/x-www-form-urlencoded')
    ]
    response = client.post(
        '/sap/oauth2/revoke',
        data=urllib.parse.urlencode(data),
        headers=headers,
    )
    assert response.status_code == 200
    assert json.loads(response.get_data(as_text=True)) == {}

    tok = db.session.query(OAuth2Token).filter(OAuth2Token.access_token == token['access_token']).one()
    assert tok.revoked is True
