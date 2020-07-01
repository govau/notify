import os
import sys

from flask import Flask
from whitenoise import WhiteNoise
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app import create_app, version


cf_app = os.environ.get('CF_APP_NAME')
sentry_dsn = os.environ.get('ADMIN_SENTRY_DSN')
sentry_env = os.environ.get('ADMIN_SENTRY_ENV')

if cf_app:
    print('cf_app: ' + cf_app)

print('sentry_dsn: ' + sentry_dsn)
print('sentry_env: ' + sentry_env)

if sentry_dsn:
    sentry_extras = dict(release=version.__commit_sha__)
    sentry_extras = {opt: val for opt, val in sentry_extras.items() if val}

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=sentry_env,
        integrations=[FlaskIntegration()],
        **sentry_extras
    )

    if cf_app:
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag('cf_app', cf_app)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'app', 'static')
STATIC_URL = 'static/'

app = Flask('app')

create_app(app)
application = WhiteNoise(app, STATIC_ROOT, STATIC_URL)
