"""
Extracts cloudfoundry config from its json and populates the environment variables that we would expect to be populated
on local/aws boxes
"""

import os
import json
import urllib.parse


def extract_cloudfoundry_config():
    vcap_services = json.loads(os.environ.get('VCAP_SERVICES', '{}'))
    set_config_env_vars(vcap_services)


def set_config_env_vars(vcap_services):
    # Handle the different CF service offerings.
    # TODO: shouldn't need the first one once we are migrated off this type.
    if 'postgres' in vcap_services:
        os.environ['SQLALCHEMY_DATABASE_URI'] = vcap_services['postgres'][0]['credentials']['uri']

    if 'postgresql' in vcap_services:
        creds = vcap_services['postgresql'][0]['credentials']
        username = creds['MASTER_USERNAME']
        password = urllib.parse.quote_plus(creds['MASTER_PASSWORD'])
        host = creds['ENDPOINT_ADDRESS']
        port = creds['PORT']
        db = creds['DB_NAME']
        os.environ['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@{host}:{port}/{db}"

    if 'redis' in vcap_services:
        creds = vcap_services['redis'][0]['credentials']
        os.environ['REDIS_URL'] = creds['url']
