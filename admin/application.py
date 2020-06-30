import os
import sys

from flask import Flask
from whitenoise import WhiteNoise
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app import create_app, version

sentry_extras = dict(release=version.__commit_sha__)
sentry_extras = {opt: val for opt, val in sentry_extras.items() if val}

print('DSN')
print(os.getenv('ADMIN_SENTRY_DSN'))
print('ENV')
print(os.getenv('ADMIN_SENTRY_ENV'))

sentry_sdk.init(
    dsn=os.getenv('ADMIN_SENTRY_DSN'),
    environment=os.getenv('ADMIN_SENTRY_ENV'),
    integrations=[FlaskIntegration()],
    **sentry_extras
)

with sentry_sdk.configure_scope() as scope:
    scope.set_tag('cf_app', os.environ.get('CF_APP_NAME'))

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'app', 'static')
STATIC_URL = 'static/'

app = Flask('app')

create_app(app)
application = WhiteNoise(app, STATIC_ROOT, STATIC_URL)
