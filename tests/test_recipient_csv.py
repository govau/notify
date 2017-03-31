import pytest
from unittest import mock
import itertools
from flask import Markup

from notifications_utils.recipients import RecipientCSV, Columns
from notifications_utils.template import Template, SMSMessageTemplate


@pytest.mark.parametrize(
    "file_contents,template_type,expected",
    [
        (
            "",
            "sms",
            [],
        ),
        (
            "phone number",
            "sms",
            [],
        ),
        (
            """
                phone number,name
                +44 123, test1
                +44 456,test2
            """,
            "sms",
            [
                [('phone number', '+44 123'), ('name', 'test1')],
                [('phone number', '+44 456'), ('name', 'test2')]
            ]
        ),
        (
            """
                email address,name
                test@example.com,test1
                test2@example.com, test2
            """,
            "email",
            [
                [('email address', 'test@example.com'), ('name', 'test1')],
                [('email address', 'test2@example.com'), ('name', 'test2')]
            ]
        ),
        (
            """
                email address
                test@example.com,test1,red
                test2@example.com, test2,blue
            """,
            "email",
            [
                [('email address', 'test@example.com'), (None, ['test1', 'red'])],
                [('email address', 'test2@example.com'), (None, ['test2', 'blue'])]
            ]
        ),
        (
            """
                email address,name
                test@example.com,"test1"
                test2@example.com," test2"
            """,
            "email",
            [
                [('email address', 'test@example.com'), ('name', 'test1')],
                [('email address', 'test2@example.com'), ('name', ' test2')]
            ]
        ),
        (
            """
                email address,date,name
                test@example.com,"Nov 28, 2016",test1
                test2@example.com,"Nov 29, 2016",test2
            """,
            "email",
            [
                [('email address', 'test@example.com'), ('date', 'Nov 28, 2016'), ('name', 'test1')],
                [('email address', 'test2@example.com'), ('date', 'Nov 29, 2016'), ('name', 'test2')]
            ]
        ),
        (
            """
                address_line_1
                Alice
                Bob
            """,
            "letter",
            [
                [('address_line_1', 'Alice')],
                [('address_line_1', 'Bob')]
            ]
        ),
        (
            """
                phone number, list, list, list
                07900900001, cat, rat, gnat
                07900900002, dog, hog, frog
                07900900003, elephant
            """,
            "sms",
            [
                [
                    ('phone number', '07900900001'),
                    ('list', ['cat', 'rat', 'gnat'])
                ],
                [
                    ('phone number', '07900900002'),
                    ('list', ['dog', 'hog', 'frog'])
                ],
                [
                    ('phone number', '07900900003'),
                    ('list', ['elephant', None, None])
                ],
            ]
        )
    ]
)
def test_get_rows(file_contents, template_type, expected):
    rows = list(RecipientCSV(file_contents, template_type=template_type).rows)
    if not expected:
        assert rows == expected
    for index, row in enumerate(expected):
        assert len(rows[index].items()) == len(row)
        for key, value in row:
            assert rows[index].get(key) == value


@pytest.mark.parametrize(
    "file_contents,template_type,expected",
    [
        (
            """
                phone number,name
                07700900460, test1
                +447700 900 460,test2
                ,
            """,
            'sms',
            [
                {
                    'columns': mock.ANY,
                    'index': 0,
                    'message_too_long': False
                },
                {
                    'columns': mock.ANY,
                    'index': 1,
                    'message_too_long': False
                },
            ]
        ),
        (
            """
                email address,name,colour
                test@example.com,test1,blue
                test2@example.com, test2,red
            """,
            'email',
            [
                {
                    'columns': mock.ANY,
                    'index': 0,
                    'message_too_long': False
                },
                {
                    'columns': mock.ANY,
                    'index': 1,
                    'message_too_long': False
                },
            ]
        )
    ]
)
def test_get_annotated_rows(file_contents, template_type, expected):
    recipients = RecipientCSV(
        file_contents,
        template_type=template_type,
        placeholders=['name'],
        max_initial_rows_shown=1
    )
    assert list(recipients.annotated_rows) == expected
    assert len(list(recipients.annotated_rows)) == 2
    assert len(list(recipients.initial_annotated_rows)) == 1
    assert not recipients.has_errors


def test_get_annotated_rows_with_errors():
    recipients = RecipientCSV(
        """
            email address, name
            a@b.com,
            a@b.com,
            a@b.com,
            a@b.com,
            a@b.com,
            a@b.com,


        """,
        template_type='email',
        placeholders=['name'],
        max_errors_shown=3
    )
    assert len(list(recipients.annotated_rows_with_errors)) == 6
    assert len(list(recipients.initial_annotated_rows_with_errors)) == 3
    assert recipients.has_errors


@pytest.mark.parametrize('template_type, row_count, header, filler, row_with_error', [
    ('email', 500, "email address\n", "test@example.com\n", "test at example dot com"),
    ('sms', 500, "phone number\n", "07900900123\n", "12345"),
])
def test_big_list_validates_right_through(template_type, row_count, header, filler, row_with_error):
    big_csv = RecipientCSV(
        header + (filler * (row_count - 1) + row_with_error),
        template_type=template_type,
        max_errors_shown=100,
        max_initial_rows_shown=3
    )
    auto_generated_row_count = RecipientCSV.max_rows / 10
    assert len(list(big_csv.annotated_rows)) == row_count
    assert big_csv.rows_with_bad_recipients == {row_count - 1}  # 0 indexed
    assert big_csv.rows_with_errors == {row_count - 1}
    assert len(list(big_csv.initial_annotated_rows_with_errors)) == 1
    assert big_csv.has_errors


def test_big_list():
    big_csv = RecipientCSV(
        "email address,name\n" + ("a@b.com\n" * RecipientCSV.max_rows),
        template_type='email',
        placeholders=['name'],
        max_errors_shown=100,
        max_initial_rows_shown=3,
        whitelist=["a@b.com"]
    )
    assert len(list(big_csv.initial_annotated_rows)) == 3
    assert len(list(big_csv.initial_annotated_rows_with_errors)) == 100
    assert len(list(big_csv.rows)) == RecipientCSV.max_rows
    assert big_csv.has_errors


@pytest.mark.parametrize(
    "file_contents,template_type,placeholders,expected_recipients,expected_personalisation",
    [
        (
            """
                phone number,name, date
                +44 123,test1,today
                +44456,    ,tomorrow
                ,,
                , ,
            """,
            'sms',
            ['name'],
            ['+44 123', '+44456'],
            [{'name': 'test1'}, {'name': ''}]
        ),
        (
            """
                email address,name,colour
                test@example.com,test1,red
                testatexampledotcom,test2,blue
            """,
            'email',
            ['colour'],
            ['test@example.com', 'testatexampledotcom'],
            [
                {'colour': 'red'},
                {'colour': 'blue'}
            ]
        ),
        (
            """
                email address
                test@example.com,test1,red
                testatexampledotcom,test2,blue
            """,
            'email',
            [],
            ['test@example.com', 'testatexampledotcom'],
            []
        )
    ]
)
def test_get_recipient(file_contents, template_type, placeholders, expected_recipients, expected_personalisation):
    recipients = RecipientCSV(file_contents, template_type=template_type, placeholders=placeholders)

    recipients_recipients = list(recipients.recipients)
    recipients_and_personalisation = list(recipients.recipients_and_personalisation)
    personalisation = list(recipients.personalisation)

    for index, row in enumerate(expected_personalisation):
        for key, value in row.items():
            assert recipients_recipients[index] == expected_recipients[index]
            assert personalisation[index].get(key) == value
            assert recipients_and_personalisation[index][1].get(key) == value


@pytest.mark.parametrize(
    "file_contents,template_type,placeholders,expected_recipients,expected_personalisation",
    [
        (
            """
                email address
                test@example.com,test1,red
                testatexampledotcom,test2,blue
            """,
            'email',
            [],
            [(1, 'test@example.com'), (2, 'testatexampledotcom')],
            []
        )
    ]
)
def test_get_recipient_respects_order(file_contents,
                                      template_type,
                                      placeholders,
                                      expected_recipients,
                                      expected_personalisation):
    recipients = RecipientCSV(file_contents, template_type=template_type, placeholders=placeholders)

    recipients_gen = recipients.enumerated_recipients_and_personalisation
    for row, email in expected_personalisation:
        assert next(recipients_gen) == (row, email, [])


@pytest.mark.parametrize(
    "file_contents,template_type,expected,expected_missing",
    [
        (
            "", 'sms', [], set(['phone number', 'name'])
        ),
        (
            """
                phone number,name
                07700900460,test1
                07700900460,test1
                07700900460,test1
            """,
            'sms',
            ['phone number', 'name'],
            set()
        ),
        (
            """
                email address,name,colour
            """,
            'email',
            ['email address', 'name', 'colour'],
            set()
        ),
        (
            """
                email address,colour
            """,
            'email',
            ['email address', 'colour'],
            set(['name'])
        ),
        (
            """
                address_line_1, address_line_2, name
            """,
            'letter',
            ['address_line_1', 'address_line_2', 'name'],
            set(['postcode', 'address line 3', 'address line 4', 'address line 5', 'address line 6'])
        ),
        (
            """
                phone number,list,list,name,list
            """,
            'sms',
            ['phone number', 'list', 'name'],
            set()
        ),
    ]
)
def test_column_headers(file_contents, template_type, expected, expected_missing):
    recipients = RecipientCSV(file_contents, template_type=template_type, placeholders=['name'])
    assert recipients.column_headers == expected
    assert recipients.missing_column_headers == expected_missing
    assert recipients.has_errors == bool(expected_missing)


@pytest.mark.parametrize(
    'placeholders',
    [
        None,
        ['name']
    ]
)
@pytest.mark.parametrize(
    'file_contents,template_type',
    [
        pytest.mark.xfail(('', 'sms')),
        pytest.mark.xfail(('name', 'sms')),
        pytest.mark.xfail(('email address', 'sms')),
        pytest.mark.xfail((
            # missing postcode
            'address_line_1, address_line_2, address_line_3, address_line_4, address_line_5',
            'letter'
        )),
        pytest.mark.xfail((
            # all address columns required, not just non-optional
            'address_line_1, postcode',
            'letter'
        )),
        ('phone number', 'sms'),
        ('phone number,name', 'sms'),
        ('email address', 'email'),
        ('email address,name', 'email'),
        ('PHONENUMBER', 'sms'),
        ('email_address', 'email'),
        (
            'address_line_1, address_line_2, address_line_3, address_line_4, address_line_5, address_line_6, postcode',
            'letter'
        ),
    ]
)
def test_recipient_column(placeholders, file_contents, template_type):
    assert RecipientCSV(file_contents, template_type=template_type, placeholders=placeholders).has_recipient_columns


@pytest.mark.parametrize(
    "file_contents,template_type,rows_with_bad_recipients,rows_with_missing_data",
    [
        (
            """
                phone number,name,date
                07700900460,test1,test1
                07700900460,test1
                +44 123,test1,test1
                07700900460,test1,test1
                07700900460,test1
                +44 123,test1,test1
                ,test1,test1
            """,
            'sms',
            {2, 5}, {1, 4, 6}
        ),
        (
            """
                phone number,name
                07700900460,test1,test2
            """,
            'sms',
            set(), set()
        ),
        (
            """
            """,
            'sms',
            set(), set()
        ),
        (
            # missing postcode
            """
                address_line_1,address_line_2,address_line_3,address_line_4,address_line_5,postcode,date
                name,          building,      street,        town,          county,        postcode,today
                name,          building,      street,        town,          county,        ,        today
            """,
            'letter',
            set(), {1}
        ),
        (
            # only required address fields
            """
                address_line_1, postcode, date
                name,           postcode, today
            """,
            'letter',
            set(), set()
        ),
    ]
)
def test_bad_or_missing_data(file_contents, template_type, rows_with_bad_recipients, rows_with_missing_data):
    recipients = RecipientCSV(file_contents, template_type=template_type, placeholders=['date'])
    assert recipients.rows_with_bad_recipients == rows_with_bad_recipients
    assert recipients.rows_with_missing_data == rows_with_missing_data
    assert recipients.has_errors is True


def test_errors_when_too_many_rows():
    recipients = RecipientCSV(
        "email address\n" + ("a@b.com\n" * (RecipientCSV.max_rows + 1)),
        template_type='email'
    )
    assert RecipientCSV.max_rows == 50000
    assert recipients.too_many_rows is True
    assert recipients.has_errors is True
    assert recipients.annotated_rows == []


@pytest.mark.parametrize(
    "file_contents,template_type,whitelist,count_of_rows_with_errors",
    [
        (
            """
                phone number
                07700900460
                07700900461
                07700900462
                07700900463
            """,
            'sms',
            ['+447700900460'],  # Same as first phone number but in different format
            3
        ),
        (
            """
                phone number
                7700900460
                447700900461
                07700900462
            """,
            'sms',
            ['07700900460', '07700900461', '07700900462', '07700900463', 'test@example.com'],
            0
        ),
        (
            """
                email address
                IN_WHITELIST@EXAMPLE.COM
                not_in_whitelist@example.com
            """,
            'email',
            ['in_whitelist@example.com', '07700900460'],  # Email case differs to the one in the CSV
            1
        )
    ]
)
def test_recipient_whitelist(file_contents, template_type, whitelist, count_of_rows_with_errors):

    recipients = RecipientCSV(
        file_contents,
        template_type=template_type,
        whitelist=whitelist
    )

    if count_of_rows_with_errors:
        assert not recipients.allowed_to_send_to
    else:
        assert recipients.allowed_to_send_to

    # Make sure the whitelist isn’t emptied by reading it. If it’s an iterator then
    # there’s a risk that it gets emptied after being read once
    recipients.whitelist = (str(fake_number) for fake_number in range(7700900888, 7700900898))
    list(recipients.whitelist)
    assert not recipients.allowed_to_send_to
    assert recipients.has_errors

    # An empty whitelist is treated as no whitelist at all
    recipients.whitelist = []
    assert recipients.allowed_to_send_to
    recipients.whitelist = itertools.chain()
    assert recipients.allowed_to_send_to


def test_detects_rows_which_result_in_overly_long_messages():
    template = SMSMessageTemplate(
        {'content': '((placeholder))', 'template_type': 'sms'},
        sender=None,
        prefix=None,
    )
    recipients = RecipientCSV(
        """
            phone number,placeholder
            07700900460,1
            07700900461,1234567890
            07700900462,12345678901
            07700900463,123456789012345678901234567890
        """,
        template_type=template.template_type,
        template=template,
        sms_character_limit=10
    )
    assert recipients.rows_with_errors == {2, 3}
    assert recipients.rows_with_message_too_long == {2, 3}
    assert recipients.has_errors


@pytest.mark.parametrize(
    "key, expected",
    sum([
        [(key, expected) for key in group] for expected, group in [
            ('07700900460', (
                'phone number',
                '   PHONENUMBER',
                'phone_number',
                'phone-number',
                'phoneNumber'
            )),
            ('Jo', (
                'FIRSTNAME',
                'first name',
                'first_name ',
                'first-name',
                'firstName'
            )),
            ('Bloggs', (
                'Last    Name',
                'LASTNAME',
                '    last_name',
                'last-name',
                'lastName   '
            ))
        ]
    ], [])
)
def test_ignores_spaces_and_case_in_placeholders(key, expected):
    recipients = RecipientCSV(
        """
            phone number,FIRSTNAME, Last Name
            07700900460, Jo, Bloggs
        """,
        placeholders=['phone_number', 'First Name', 'lastname'],
        template_type='sms'
    )
    first_row = list(recipients.annotated_rows)[0]
    assert first_row['columns'].get(key)['data'] == expected
    assert first_row['columns'][key]['data'] == expected
    assert list(recipients.personalisation)[0][key] == expected
    assert list(recipients.recipients) == ['07700900460']
    assert len(first_row['columns'].items()) == 3
    assert not recipients.has_errors

    assert recipients.missing_column_headers == set()
    recipients.placeholders = {'one', 'TWO', 'Thirty_Three'}
    assert recipients.missing_column_headers == {'one', 'TWO', 'Thirty_Three'}
    assert recipients.has_errors


def test_error_if_too_many_recipients():
    recipients = RecipientCSV(
        'phone number,\n07700900460,\n07700900460,\n07700900460,',
        placeholders=['phone_number'],
        template_type='sms',
        remaining_messages=2
    )
    assert recipients.has_errors
    assert recipients.more_rows_than_can_send


def test_dont_error_if_too_many_recipients_not_specified():
    recipients = RecipientCSV(
        'phone number,\n07700900460,\n07700900460,\n07700900460,',
        placeholders=['phone_number'],
        template_type='sms'
    )
    assert not recipients.has_errors
    assert not recipients.more_rows_than_can_send
