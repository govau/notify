##!/usr/bin/env python
from __future__ import print_function

import os
from flask import Flask
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app import create_app, version

sentry_extras = dict(release=version.__commit_sha__)
sentry_extras = {opt: val for opt, val in sentry_extras.items() if val}

sentry_sdk.init(
    dsn=os.getenv("API_SENTRY_DSN"),
    environment=os.getenv("API_SENTRY_ENV"),
    integrations=[FlaskIntegration()],
    **sentry_extras
)

with sentry_sdk.configure_scope() as scope:
    scope.set_tag("cf_app", os.environ.get('CF_APP_NAME'))

application = Flask('app')
application = create_app(application)
