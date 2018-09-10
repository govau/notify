from flask import json


def test_get_status_all_ok(client):
    path = '/_status'
    response = client.get(path)
    assert response.status_code == 200
    resp_json = json.loads(response.get_data(as_text=True))
    assert resp_json['status'] == 'ok'
    assert resp_json['db_version']
    assert resp_json['commit_sha']
    assert resp_json['build_number']
    assert resp_json['build_time']
