import pytest
import mock
import itertools
from flask import Markup

from notifications_utils.recipients import RecipientCSV, Columns
from notifications_utils.template import Template


@pytest.mark.parametrize(
    "file_contents,template_type,expected",
    [
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
        )
    ]
)
def test_get_rows(file_contents, template_type, expected):
    rows = list(RecipientCSV(file_contents, template_type=template_type).rows)
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


def test_big_list():
    big_csv = RecipientCSV(
        "email address,name\n" + ("a@b.com\n"*100000),
        template_type='email',
        placeholders=['name'],
        max_errors_shown=100,
        max_initial_rows_shown=3
    )
    assert len(list(big_csv.initial_annotated_rows)) == 3
    assert len(list(big_csv.initial_annotated_rows_with_errors)) == 100
    assert len(list(big_csv.rows)) == 100000
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
    "file_contents,template_type,expected,expected_highlighted,expected_missing",
    [
        (
            "", 'sms', [], [], set(['phone number', 'name'])
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
            ['phone number', Markup('<span class=\'placeholder\'>name</span>')],
            set()
        ),
        (
            """
                email address,name,colour
            """,
            'email',
            ['email address', 'name', 'colour'],
            ['email address', Markup('<span class=\'placeholder\'>name</span>'), 'colour'],
            set()
        ),
        (
            """
                email address,colour
            """,
            'email',
            ['email address', 'colour'],
            ['email address', 'colour'],
            set(['name'])
        )
    ]
)
def test_column_headers(file_contents, template_type, expected, expected_highlighted, expected_missing):
    recipients = RecipientCSV(file_contents, template_type=template_type, placeholders=['name'])
    assert recipients.column_headers == expected
    assert recipients.column_headers_with_placeholders_highlighted == expected_highlighted
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
        ('phone number', 'sms'),
        ('phone number,name', 'sms'),
        ('email address', 'email'),
        ('email address,name', 'email'),
        ('PHONENUMBER', 'sms'),
        ('email_address', 'email')
    ]
)
def test_recipient_column(placeholders, file_contents, template_type):
    assert RecipientCSV(file_contents, template_type=template_type, placeholders=placeholders).has_recipient_column


@pytest.mark.parametrize(
    "file_contents,rows_with_bad_recipients,rows_with_missing_data",
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
            """,
            {2, 5}, {1, 4}
        ),
        (
            """
                phone number,name
                07700900460,test1,test2
            """,
            set(), set()
        ),
        (
            """
            """,
            set(), set()
        )
    ]
)
def test_bad_or_missing_data(file_contents, rows_with_bad_recipients, rows_with_missing_data):
    recipients = RecipientCSV(file_contents, template_type='sms', placeholders=['date'])
    assert recipients.rows_with_bad_recipients == rows_with_bad_recipients
    assert recipients.rows_with_missing_data == rows_with_missing_data
    assert recipients.has_errors is True


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
    recipients = RecipientCSV(
        """
            phone number,placeholder
            07700900460,1
            07700900461,1234567890
            07700900462,12345678901
            07700900463,123456789012345678901234567890
        """,
        template_type='sms',
        template=Template({'content': '((placeholder))', 'type': 'sms'}, content_character_limit=10)
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
