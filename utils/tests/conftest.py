import pytest
from flask import Flask

import requests_mock


class FakeService():
    id = "1234"


@pytest.fixture
def app():
    flask_app = Flask(__name__)
    ctx = flask_app.app_context()
    ctx.push()

    yield flask_app

    ctx.pop()


@pytest.fixture(scope='session')
def sample_service():
    return FakeService()


@pytest.yield_fixture
def rmock():
    with requests_mock.mock() as rmock:
        yield rmock
