##!/usr/bin/env python
from __future__ import print_function

import os
from flask import Flask
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app import create_app

sentry_sdk.init(
    dsn=os.getenv("API_SENTRY_DSN"),
    environment=os.getenv("API_SENTRY_ENV"),
    integrations=[FlaskIntegration()]
)

application = Flask('app')

create_app(application)
