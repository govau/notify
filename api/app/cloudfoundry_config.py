"""
Extracts cloudfoundry config from its json and populates the environment variables that we would expect to be populated
on local/aws boxes
"""

import os
import json


def extract_cloudfoundry_config():
    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    vcap_application = json.loads(os.environ.get('VCAP_APPLICATION'))
    set_config_env_vars(vcap_services, vcap_application)


def set_config_env_vars(vcap_services, vcap_application):
    # Postgres config
    os.environ['SQLALCHEMY_DATABASE_URI'] = vcap_services['postgres'][0]['credentials']['uri']
    os.environ['APP_NAME'] = vcap_application['application_name']
