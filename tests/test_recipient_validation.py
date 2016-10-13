import re
import pytest
from notifications_utils.recipients import (
    validate_phone_number,
    format_phone_number,
    validate_and_format_phone_number,
    InvalidPhoneError,
    validate_email_address,
    InvalidEmailError,
    allowed_to_send_to
)


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

valid_email_addresses = (
    'email@domain.com',
    'email@domain.COM',
    'firstname.lastname@domain.com',
    'email@subdomain.domain.com',
    'firstname+lastname@domain.com',
    '1234567890@domain.com',
    'email@domain-one.com',
    '_______@domain.com',
    'email@domain.name',
    'email@domain.co.jp',
    'firstname-lastname@domain.com',
    '#%^%#$@#$#.com',
)
invalid_email_addresses = (
    'email@123.123.123.123',
    'email@[123.123.123.123]',
    'plainaddress',
    '@no-local-part.com',
    'Outlook Contact <outlook-contact@domain.com>',
    'no-at.domain.com',
    'no-tld@domain',
    'middle-semicolon@domain.co;uk',
    'trailing-semicolon@domain.com;',
    '"email+leading-quotes@domain.com',
    'email+middle"-quotes@domain.com',
    '"quoted-local-part"@domain.com',
    '"quoted@domain.com"',
    'lots-of-dots@domain..gov..uk',
    'multiple@domains@domain.com',
    'spaces in local@domain.com',
    'spaces-in-domain@dom ain.com',
    'underscores-in-domain@dom_ain.com',
    # this is technically valid (and accepted by SES), however we have made a conscious decision to block it
    # to keep validation leaner
    'technically..valid@domain.com',
)


@pytest.mark.parametrize("phone_number", valid_phone_numbers)
def test_phone_number_accepts_valid_values(phone_number):
    try:
        validate_phone_number(phone_number)
    except InvalidPhoneError:
        pytest.fail('Unexpected InvalidPhoneError')


@pytest.mark.parametrize("phone_number", valid_phone_numbers)
def test_valid_phone_number_can_be_formatted_consistently(phone_number):
    assert format_phone_number(validate_phone_number(phone_number)) == '+447123456789'
    assert validate_and_format_phone_number(phone_number) == '+447123456789'
    assert validate_and_format_phone_number(phone_number, human_readable=True) == '07123 456 789'


@pytest.mark.parametrize("phone_number, error_message", invalid_phone_numbers)
def test_phone_number_rejects_invalid_values(phone_number, error_message):
    with pytest.raises(InvalidPhoneError) as e:
        validate_phone_number(phone_number)
    assert error_message == str(e.value)


@pytest.mark.parametrize("email_address", valid_email_addresses)
def test_validate_email_address_accepts_valid(email_address):
    assert validate_email_address(email_address) == email_address


@pytest.mark.parametrize("email_address", invalid_email_addresses)
def test_validate_email_address_raises_for_invalid(email_address):
    with pytest.raises(InvalidEmailError) as e:
        validate_email_address(email_address)


@pytest.mark.parametrize("phone_number", valid_phone_numbers)
def test_validates_against_whitelist_of_phone_numbers(phone_number):
    assert allowed_to_send_to(phone_number, ['07123456789', '07700900460', 'test@example.com'])
    assert not allowed_to_send_to(phone_number, ['07700900460', '07700900461', 'test@example.com'])


@pytest.mark.parametrize("email_address", valid_email_addresses)
def test_validates_against_whitelist_of_email_addresses(email_address):
    assert not allowed_to_send_to(email_address, ['very_special_and_unique@example.com'])
