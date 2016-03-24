import re
import pytest
from utils.recipients import validate_phone_number, InvalidPhoneError, validate_email_address, InvalidEmailError


valid_phone_numbers = [
    '7123456789',
    '07123456789',
    '07123 456789',
    '07123-456-789',
    '00447123456789',
    '00 44 7123456789',
    '+447123456789',
    '+44 7123 456 789',
    '+44 (0)7123 456 789'
]

invalid_phone_numbers = sum([
    [
        (phone_number, error) for phone_number in group
    ] for error, group in [
        ('Too many digits', (
            '0712345678910',
            '0044712345678910',
            '0044712345678910',
            '+44 (0)7123 456 789 10',
        )),
        ('Not enough digits', (
            '0712345678',
            '004471234567',
            '00447123456',
            '+44 (0)7123 456 78',
        )),
        ('Not a UK mobile number', (
            '08081 570364',
            '+44 8081 570364',
            '0117 496 0860',
            '+44 117 496 0860',
            '020 7946 0991',
            '+44 20 7946 0991',
        )),
        ('Must not contain letters or symbols', (
            '07890x32109',
            '07123 456789...',
            '07123 ☟☜⬇⬆☞☝',
            '07123☟☜⬇⬆☞☝',
            '07";DROP TABLE;"',
            '+44 07ab cde fgh',
        ))
    ]
], [])

email_addresses = sum([
    [
        (email_address, valid) for email_address in group
    ] for valid, group in [
        (True, (
            'email@domain.com',
            'firstname.lastname@domain.com',
            'email@subdomain.domain.com',
            'firstname+lastname@domain.com',
            'email@123.123.123.123',
            'email@[123.123.123.123]',
            '"email"@domain.com',
            '1234567890@domain.com',
            'email@domain-one.com',
            '_______@domain.com',
            'email@domain.name',
            'email@domain.co.jp',
            'firstname-lastname@domain.com'
        )),
        (False, (
            'plainaddress',
            '#@%^%#$@#$@#.com',
            '@domain.com',
            'Jo Smith <email@domain.com>',
            'email.domain.com',
            'email@domain@domain.com',
            'email@domain',
        ))
    ]
], [])


@pytest.mark.parametrize("phone_number", valid_phone_numbers)
def test_phone_number_accepts_valid_values(phone_number):
    try:
        validate_phone_number(phone_number)
    except InvalidPhoneError:
        pytest.fail('Unexpected InvalidPhoneError')


@pytest.mark.parametrize("phone_number, error_message", invalid_phone_numbers)
def test_phone_number_rejects_invalid_values(phone_number, error_message):
    with pytest.raises(InvalidPhoneError) as e:
        validate_phone_number(phone_number)
    assert error_message == str(e.value)


@pytest.mark.parametrize("email_address,is_valid", email_addresses)
def test_validates_email_addresses(email_address, is_valid):
    if is_valid:
        validate_email_address(email_address)
    else:
        with pytest.raises(InvalidEmailError) as e:
            validate_email_address(email_address)
