import os
import json


def extract_predefined_queues():
    url = os.environ.get('SQS_QUEUE_URL', '')
    key = os.environ.get('SQS_AWS_ACCESS_KEY_ID', '')
    secret = os.environ.get('SQS_AWS_SECRET_ACCESS_KEY', '')
    if url and key and secret:
        return single_queue_predefined_queues(url, key, secret, os.getenv('QUEUE_PREFIX', ''))

    vcap_services = json.loads(os.environ.get('VCAP_SERVICES', '{}'))

    return cf_predefined_queues(vcap_services)


def single_queue_predefined_queues(queue_url, key, secret, queue_name_prefix):
    queues = {}

    # TODO: use QueueNames.all_queues() which requires moving QueueNames in here
    # and refactoring all app.config imports to app.queue_config.
    for i, queue_name in enumerate([
        'periodic-tasks',
        'priority-tasks',
        'database-tasks',
        'send-sms-tasks',
        'send-email-tasks',
        'research-mode-tasks',
        'statistics-tasks',
        'job-tasks',
        'retry-tasks',
        'notify-internal-tasks',
        'process-ftp-tasks',
        'create-letters-pdf-tasks',
        'service-callbacks',
        'letter-tasks',
        'antivirus-tasks',
    ]):
        queues[f"{queue_name_prefix}{queue_name}"] = {
            'url': queue_url,
            'access_key_id': key,
            'secret_access_key': secret,
        }

    return queues


def cf_predefined_queues(vcap_services):
    queues = {}

    if 'sqs' not in vcap_services:
        return queues

    for i, service in enumerate(vcap_services['sqs']):
        queues[trim_prefix(service['name'], os.environ.get('CF_SERVICE_QUEUE_PREFIX', ''))] = {
            'url': service['credentials']['QUEUE_URL'],
            'access_key_id': service['credentials']['SQS_AWS_ACCESS_KEY_ID'],
            'secret_access_key': service['credentials']['SQS_AWS_SECRET_ACCESS_KEY'],
        }

    return queues


def trim_prefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s
