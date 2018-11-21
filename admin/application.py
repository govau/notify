import os

from flask import Flask
from whitenoise import WhiteNoise
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app import create_app

sentry_sdk.init(
    dsn=os.getenv("ADMIN_SENTRY_DSN"),
    environment=os.getenv("ADMIN_SENTRY_ENV"),
    integrations=[FlaskIntegration()]
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'app', 'static')
STATIC_URL = 'static/'

app = Flask('app')

create_app(app)
application = WhiteNoise(app, STATIC_ROOT, STATIC_URL)

with sentry_sdk.configure_scope() as scope:
    scope.set_tag("app_name", os.environ['APP_NAME'])
