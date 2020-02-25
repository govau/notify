import json
import pytest

from app.queue_config import extract_predefined_queues


@pytest.fixture
def sqs_config():
    return [
        {
            'name': 'notify-sqs-testing-priority-tasks',
            'credentials': {
                'QUEUE_URL': 'url',
                'SQS_AWS_ACCESS_KEY_ID': 'key',
                'SQS_AWS_SECRET_ACCESS_KEY': 'secret',
            },
        },
    ]


@pytest.fixture
def cloudfoundry_config(sqs_config):
    return {
        'sqs': sqs_config,
        'user-provided': []
    }


@pytest.fixture
def cloudfoundry_environ(monkeypatch, cloudfoundry_config):
    monkeypatch.setenv('VCAP_SERVICES', json.dumps(cloudfoundry_config))
    monkeypatch.setenv('VCAP_APPLICATION', '{"space_name": "🚀🌌"}')


@pytest.fixture
def single_queue_environ(monkeypatch):
    monkeypatch.setenv('SQS_QUEUE_URL', 'https://sqs.ap-southeast-2.amazonaws.com/single-queue-url')
    monkeypatch.setenv('SQS_AWS_ACCESS_KEY_ID', 'single-queue-key')
    monkeypatch.setenv('SQS_AWS_SECRET_ACCESS_KEY', 'single-queue-secret')


@pytest.fixture
def no_single_queue_environ(monkeypatch):
    monkeypatch.setenv('SQS_QUEUE_URL', '')
    monkeypatch.setenv('SQS_AWS_ACCESS_KEY_ID', '')
    monkeypatch.setenv('SQS_AWS_SECRET_ACCESS_KEY', '')


@pytest.mark.usefixtures('cloudfoundry_environ', 'no_single_queue_environ')
def test_extract_predefined_queues_for_cf():
    queues = extract_predefined_queues()

    assert queues == {
        'testing-priority-tasks': {
            'url': 'url',
            'access_key_id': 'key',
            'secret_access_key': 'secret',
        },
    }


@pytest.mark.usefixtures('single_queue_environ')
def test_extract_predefined_queues_for_single_queue():
    queues = extract_predefined_queues()

    assert len(queues) == 16

    assert queues['testing-priority-tasks'] == {
        'url': 'https://sqs.ap-southeast-2.amazonaws.com/single-queue-url',
        'access_key_id': 'single-queue-key',
        'secret_access_key': 'single-queue-secret',
    }


@pytest.mark.usefixtures('cloudfoundry_environ', 'single_queue_environ')
def test_extract_predefined_queues_for_single_queue_overrides_cf():
    queues = extract_predefined_queues()

    assert len(queues) == 16

    assert queues['testing-priority-tasks'] == {
        'url': 'https://sqs.ap-southeast-2.amazonaws.com/single-queue-url',
        'access_key_id': 'single-queue-key',
        'secret_access_key': 'single-queue-secret',
    }
