import pytest

from functools import partial

from notifications_utils.recipients import (
    validate_phone_number,
    validate_and_format_phone_number,
    InvalidPhoneError,
    validate_email_address,
    InvalidEmailError,
    allowed_to_send_to,
    InvalidAddressError,
    validate_recipient,
    is_uk_phone_number,
    normalise_phone_number,
    international_phone_info,
    get_international_phone_info,
    format_phone_number_human_readable,
    format_recipient,
    try_validate_and_format_phone_number
)


valid_uk_phone_numbers = [
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


valid_international_phone_numbers = [
    '71234567890',  # Russia
    '1-202-555-0104',  # USA
    '+12025550104',  # USA
    '0012025550104',  # USA
    '+0012025550104',  # USA
    '23051234567',  # Mauritius,
    '+682 12345',  # Cook islands
    '+3312345678',
    '003312345678'
]


valid_phone_numbers = valid_uk_phone_numbers + valid_international_phone_numbers


invalid_uk_phone_numbers = sum([
    [
        (phone_number, error) for phone_number in group
    ] for error, group in [
        ('Too many digits', (
            '712345678910',
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
            'ALPHANUM3R1C',
        ))
    ]
], [])


invalid_phone_numbers = list(filter(
    lambda number: number[0] not in {
        '712345678910',   # Could be Russia
    },
    invalid_uk_phone_numbers
)) + [
    ('800000000000', 'Not a valid country prefix'),
    ('1234567', 'Not enough digits'),
    ('+682 1234', 'Not enough digits'),  # Cook Islands phone numbers can be 5 digits
]


valid_email_addresses = (
    'email@domain.com',
    'email@domain.COM',
    'firstname.lastname@domain.com',
    'firstname.o\'lastname@domain.com',
    'email@subdomain.domain.com',
    'firstname+lastname@domain.com',
    '1234567890@domain.com',
    'email@domain-one.com',
    '_______@domain.com',
    'email@domain.name',
    'email@domain.superlongtld',
    'email@domain.co.jp',
    'firstname-lastname@domain.com',
    'info@german-financial-services.vermögensberatung',
    'info@german-financial-services.reallylongarbitrarytldthatiswaytoohugejustincase',
    'japanese-info@例え.テスト',
    'technically..valid@domain.com',
)
invalid_email_addresses = (
    'email@123.123.123.123',
    'email@[123.123.123.123]',
    'plainaddress',
    '@no-local-part.com',
    'Outlook Contact <outlook-contact@domain.com>',
    'no-at.domain.com',
    'no-tld@domain',
    ';beginning-semicolon@domain.co.uk',
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
    'pipe-in-domain@example.com|gov.uk',
    'comma,in-local@gov.uk',
    'comma-in-domain@domain,gov.uk',
    'pound-sign-in-local£@domain.com',
    'local-with-’-apostrophe@domain.com',
    'local-with-”-quotes@domain.com',
    'domain-starts-with-a-dot@.domain.com',
)


@pytest.mark.parametrize("phone_number", valid_international_phone_numbers)
def test_detect_international_phone_numbers(phone_number):
    assert is_uk_phone_number(phone_number) is False


@pytest.mark.parametrize("phone_number", valid_uk_phone_numbers)
def test_detect_uk_phone_numbers(phone_number):
    assert is_uk_phone_number(phone_number) is True


@pytest.mark.parametrize("phone_number, expected_info", [
    ('07900900123', international_phone_info(
        international=False,
        country_prefix='44',  # UK
        billable_units=1,
    )),
    ('20-12-1234-1234', international_phone_info(
        international=True,
        country_prefix='20',  # Egypt
        billable_units=3,
    )),
    ('00201212341234', international_phone_info(
        international=True,
        country_prefix='20',  # Egypt
        billable_units=3,
    )),
    ('1664000000000', international_phone_info(
        international=True,
        country_prefix='1664',  # Montserrat
        billable_units=1,
    )),
    ('71234567890', international_phone_info(
        international=True,
        country_prefix='7',  # Russia
        billable_units=1,
    )),
    ('1-202-555-0104', international_phone_info(
        international=True,
        country_prefix='1',  # USA
        billable_units=1,
    )),
    ('+23051234567', international_phone_info(
        international=True,
        country_prefix='230',  # Mauritius
        billable_units=2,
    ))
])
def test_get_international_info(phone_number, expected_info):
    assert get_international_phone_info(phone_number) == expected_info


@pytest.mark.parametrize('phone_number', [
    'abcd',
    '079OO900123',
    pytest.mark.xfail(''),
    pytest.mark.xfail('12345'),
    pytest.mark.xfail('+12345'),
    pytest.mark.xfail('1-2-3-4-5'),
    pytest.mark.xfail('1 2 3 4 5'),
    pytest.mark.xfail('(1)2345'),
])
def test_normalise_phone_number_raises_if_unparseable_characters(phone_number):
    with pytest.raises(InvalidPhoneError):
        normalise_phone_number(phone_number)


@pytest.mark.parametrize('phone_number', [
    '+21 4321 0987',
    '00997 1234 7890',
    '801234-7890'
    '(8-0)-1234-7890',
])
def test_get_international_info_raises(phone_number):
    with pytest.raises(InvalidPhoneError) as error:
        get_international_phone_info(phone_number)
    assert str(error.value) == 'Not a valid country prefix'


@pytest.mark.parametrize("phone_number", valid_uk_phone_numbers)
@pytest.mark.parametrize("validator", [
    partial(validate_recipient, template_type='sms'),
    partial(validate_recipient, template_type='sms', international_sms=False),
    partial(validate_phone_number),
    partial(validate_phone_number, international=False),
])
def test_phone_number_accepts_valid_values(validator, phone_number):
    try:
        validator(phone_number)
    except InvalidPhoneError:
        pytest.fail('Unexpected InvalidPhoneError')


@pytest.mark.parametrize("phone_number", valid_phone_numbers)
@pytest.mark.parametrize("validator", [
    partial(validate_recipient, template_type='sms', international_sms=True),
    partial(validate_phone_number, international=True),
])
def test_phone_number_accepts_valid_international_values(validator, phone_number):
    try:
        validator(phone_number)
    except InvalidPhoneError:
        pytest.fail('Unexpected InvalidPhoneError')


@pytest.mark.parametrize("phone_number", valid_uk_phone_numbers)
def test_valid_uk_phone_number_can_be_formatted_consistently(phone_number):
    assert validate_and_format_phone_number(phone_number) == '447123456789'


@pytest.mark.parametrize("phone_number, expected_formatted", [
    ('71234567890', '71234567890'),
    ('1-202-555-0104', '12025550104'),
    ('+12025550104', '12025550104'),
    ('0012025550104', '12025550104'),
    ('+0012025550104', '12025550104'),
    ('23051234567', '23051234567'),
])
def test_valid_international_phone_number_can_be_formatted_consistently(phone_number, expected_formatted):
    assert validate_and_format_phone_number(
        phone_number, international=True
    ) == expected_formatted


@pytest.mark.parametrize("phone_number, error_message", invalid_uk_phone_numbers)
@pytest.mark.parametrize("validator", [
    partial(validate_recipient, template_type='sms'),
    partial(validate_recipient, template_type='sms', international_sms=False),
    partial(validate_phone_number),
    partial(validate_phone_number, international=False),
])
def test_phone_number_rejects_invalid_values(validator, phone_number, error_message):
    with pytest.raises(InvalidPhoneError) as e:
        validator(phone_number)
    assert error_message == str(e.value)


@pytest.mark.parametrize("phone_number, error_message", invalid_phone_numbers)
@pytest.mark.parametrize("validator", [
    partial(validate_recipient, template_type='sms', international_sms=True),
    partial(validate_phone_number, international=True),
])
def test_phone_number_rejects_invalid_international_values(validator, phone_number, error_message):
    with pytest.raises(InvalidPhoneError) as e:
        validator(phone_number)
    assert error_message == str(e.value)


@pytest.mark.parametrize("email_address", valid_email_addresses)
def test_validate_email_address_accepts_valid(email_address):
    try:
        assert validate_email_address(email_address) == email_address
    except InvalidEmailError:
        pytest.fail('Unexpected InvalidEmailError')


def test_validate_email_address_strips_whitespace():
    assert validate_email_address('email@domain.com ') == 'email@domain.com'


@pytest.mark.parametrize("email_address", invalid_email_addresses)
def test_validate_email_address_raises_for_invalid(email_address):
    with pytest.raises(InvalidEmailError) as e:
        validate_email_address(email_address)
    assert str(e.value) == 'Not a valid email address'


@pytest.mark.parametrize('column', [
    'address_line_1', 'AddressLine1',
    'postcode', 'Postcode'
])
@pytest.mark.parametrize('contents', [
    '', ' ', None
])
def test_validate_address_raises_for_missing_required_columns(column, contents):
    with pytest.raises(InvalidAddressError) as e:
        validate_recipient(contents, 'letter', column=column)
    assert 'Missing' == str(e.value)


@pytest.mark.parametrize('column', [
    'address_line_3',
    'address_line_4',
    'address_line_5',
    'address_line_6',
])
def test_validate_address_doesnt_raise_for_missing_optional_columns(column):
    assert validate_recipient('', 'letter', column=column) == ''


def test_validate_address_raises_for_wrong_column():
    with pytest.raises(TypeError):
        validate_recipient('any', 'letter', column='email address')


@pytest.mark.parametrize('column', [
    'address_line_1',
    'address_line_2',
    'address_line_3',
    'address_line_4',
    'address_line_5',
    'postcode',
])
def test_validate_address_allows_any_non_empty_value(column):
    assert validate_recipient('any', 'letter', column=column) == 'any'


@pytest.mark.parametrize('column', [
    'address_line_1',
    'address_line_2',
    'address_line_3',
    'address_line_4',
    'address_line_5',
    'address_line_6',
    'postcode',
])
def test_non_ascii_address_line_raises_invalid_address_error(column):
    invalid_address = u'\u041F\u0435\u0442\u044F'
    with pytest.raises(InvalidAddressError) as e:
        validate_recipient(invalid_address, 'letter', column=column)
    assert str(e.value) == u'Can’t include \u041F, \u0435, \u0442 or \u044F'


def test_valid_address_line_does_not_raise_error():
    invalid_address = u'Fran\u00e7oise'
    assert validate_recipient(invalid_address, 'letter', column='address_line_1')


@pytest.mark.parametrize("phone_number", valid_uk_phone_numbers)
def test_validates_against_whitelist_of_phone_numbers(phone_number):
    assert allowed_to_send_to(phone_number, ['07123456789', '07700900460', 'test@example.com'])
    assert not allowed_to_send_to(phone_number, ['07700900460', '07700900461', 'test@example.com'])


@pytest.mark.parametrize("email_address", valid_email_addresses)
def test_validates_against_whitelist_of_email_addresses(email_address):
    assert not allowed_to_send_to(email_address, ['very_special_and_unique@example.com'])


@pytest.mark.parametrize("phone_number, expected_formatted", [
    ('07900900123', '07900 900123'),  # UK
    ('+44(0)7900900123', '07900 900123'),  # UK
    ('447900900123', '07900 900123'),  # UK
    ('20-12-1234-1234', '+20 121 234 1234'),  # Egypt
    ('00201212341234', '+20 121 234 1234'),  # Egypt
    ('1664 0000000', '+1 664-000-0000'),  # Montserrat
    ('7 499 1231212', '+7 499 123-12-12'),  # Moscow (Russia)
    ('1-202-555-0104', '+1 202-555-0104'),  # Washington DC (USA)
    ('+23051234567', '+230 5123 4567'),  # Mauritius
    ('33(0)1 12345678', '+33 1 12 34 56 78'),  # Paris (France)
    ('33(0)1 12 34 56 78 90 12 34', '+33 112345678901234'),  # Long, not real, number
])
def test_format_uk_and_international_phone_numbers(phone_number, expected_formatted):
    assert format_phone_number_human_readable(phone_number) == expected_formatted


@pytest.mark.parametrize("recipient, expected_formatted", [
    (True, ''),
    (False, ''),
    (0, ''),
    (0.1, ''),
    (None, ''),
    ('foo', 'foo'),
    ('TeSt@ExAmPl3.com', 'test@exampl3.com'),
    ('+4407900 900 123', '447900900123'),
    ('+1 800 555 5555', '+1 800 555 5555'),
])
def test_format_recipient(recipient, expected_formatted):
    assert format_recipient(recipient) == expected_formatted


def test_try_format_recipient_doesnt_throw():
    assert try_validate_and_format_phone_number('ALPHANUM3R1C') == 'ALPHANUM3R1C'


def test_format_phone_number_human_readable_doenst_throw():
    assert format_phone_number_human_readable('ALPHANUM3R1C') == 'ALPHANUM3R1C'
