import pytest
from notifications_utils.field import str2bool


@pytest.mark.parametrize(
    "value", [
        '0',
        0, 2, 99.99999,
        'off',
        'exclude',
        'no'
        'any random string',
        'false',
        False,
        [], {}, (),
        ['true'], {'True': True}, (True, 'true', 1)
    ]
)
def test_what_will_not_trigger_optional_placeholder(value):
    assert str2bool(value) is False


@pytest.mark.parametrize(
    "value", [
        1,
        '1',
        'yes',
        'y',
        'true',
        'True',
        True,
        'include',
        'show'
    ]
)
def test_what_will_trigger_optional_placeholder(value):
    assert str2bool(value) is True
