"""
Extracts cloudfoundry config from its json and populates the environment variables that we would expect to be populated
on local/aws boxes
"""

import os
import json


def extract_cloudfoundry_config():
    vcap_services = json.loads(os.environ.get('VCAP_SERVICES', '{}'))

    set_config_env_vars(vcap_services)


def set_config_env_vars(vcap_services):
    if 'postgres' in vcap_services:
        os.environ['SQLALCHEMY_DATABASE_URI'] = vcap_services['postgres'][0]['credentials']['uri']
