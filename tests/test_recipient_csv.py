import pytest
import itertools
from flask import Markup

from utils.recipients import RecipientCSV


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
                {'phone number': '+44 123', 'name': 'test1'},
                {'phone number': '+44 456', 'name': 'test2'}
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
                {'email address': 'test@example.com', 'name': 'test1'},
                {'email address': 'test2@example.com', 'name': 'test2'}
            ]
        )
    ]
)
def test_get_rows(file_contents, template_type, expected):
    assert list(RecipientCSV(file_contents, template_type=template_type).rows) == expected


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
                    'phone number': {'data': '07700900460', 'error': None, 'ignore': False},
                    'name': {'data': 'test1', 'error': None, 'ignore': False},
                    'index': 0
                },
                {
                    'phone number': {'data': '+447700 900 460', 'error': None, 'ignore': False},
                    'name': {'data': 'test2', 'error': None, 'ignore': False},
                    'index': 1
                },
            ]
        ),
        (
            """
                email address,name,colour
                test@example.com,test1,blue
                example.com, test2,red
            """,
            'email',
            [
                {
                    'email address': {'data': 'test@example.com', 'error': None, 'ignore': False},
                    'name': {'data': 'test1', 'error': None, 'ignore': False},
                    'colour': {'data': 'blue', 'error': None, 'ignore': True},
                    'index': 0
                },
                {
                    'email address': {'data': 'example.com', 'error': 'Not a valid email address', 'ignore': False},
                    'name': {'data': 'test2', 'error': None, 'ignore': False},
                    'colour': {'data': 'red', 'error': None, 'ignore': True},
                    'index': 1
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
        )
    ]
)
def test_get_recipient(file_contents, template_type, placeholders, expected_recipients, expected_personalisation):
    recipients = RecipientCSV(file_contents, template_type=template_type, placeholders=placeholders)
    assert list(recipients.recipients) == expected_recipients
    assert list(recipients.personalisation) == expected_personalisation
    assert list(recipients.recipients_and_personalisation) == [
        (recipient, personalisation)
        for recipient, personalisation in zip(expected_recipients, expected_personalisation)
    ]


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
    assert len(recipients.rows_with_errors) == count_of_rows_with_errors

    recipients.whitelist = []
    assert len(recipients.rows_with_errors) == 0

    recipients.whitelist = itertools.chain()
    assert len(recipients.rows_with_errors) == 0
