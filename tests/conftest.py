import pytest
from flask import Flask


@pytest.fixture
def app():
    return Flask(__name__)
