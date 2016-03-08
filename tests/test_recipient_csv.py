import pytest
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
def test_get_rows_annotated_and_truncated(file_contents, template_type, expected):
    assert list(RecipientCSV(
        file_contents,
        template_type=template_type,
        placeholders=['name']
    ).rows_annotated_and_truncated) == expected


def test_limited_number_errors():
    assert len(list(RecipientCSV(
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
        max_errors_shown=3,
        max_initial_rows_shown=1
    ).rows_annotated_and_truncated)) == 3


def test_limited_number_errors_and_limited_number_displayed():
    assert list(RecipientCSV(
        """
            email address, name
            a@b.com,
            a@b.com,
            a@b.com, show this name
            a@b.com,
            a@b.com,
            a@b.com,
            a@b.com, don’t show this name
            a@b.com,
            a@b.com,
            a@b.com,
        """,
        template_type='email',
        placeholders=['name'],
        max_errors_shown=5,
        max_initial_rows_shown=3
    ).rows_annotated_and_truncated) == [
        {
            'email address': {'data': 'a@b.com', 'error': None, 'ignore': False},
            'name': {'data': '', 'error': 'Missing', 'ignore': False},
            'index': 0
        },
        {
            'email address': {'data': 'a@b.com', 'error': None, 'ignore': False},
            'name': {'data': '', 'error': 'Missing', 'ignore': False},
            'index': 1
        },
        {
            'email address': {'data': 'a@b.com', 'error': None, 'ignore': False},
            'name': {'data': 'show this name', 'error': None, 'ignore': False},
            'index': 2
        },
        {
            'email address': {'data': 'a@b.com', 'error': None, 'ignore': False},
            'name': {'data': '', 'error': 'Missing', 'ignore': False},
            'index': 3
        },
        {
            'email address': {'data': 'a@b.com', 'error': None, 'ignore': False},
            'name': {'data': '', 'error': 'Missing', 'ignore': False},
            'index': 4
        },
        {
            'email address': {'data': 'a@b.com', 'error': None, 'ignore': False},
            'name': {'data': '', 'error': 'Missing', 'ignore': False},
            'index': 5
        },
    ]


def test_big_list():
    big_csv = RecipientCSV(
        "email address,name\n" + ("a@b.com\n"*100000),
        template_type='email',
        placeholders=['name'],
        max_errors_shown=100,
        max_initial_rows_shown=3
    )
    assert len(list(big_csv.rows_annotated_and_truncated)) == 100
    assert len(list(big_csv.rows)) == 100000


@pytest.mark.parametrize(
    "file_contents,template_type,placeholders,expected_recipients,expected_personalisation",
    [
        (
            """
                phone number,name, date
                +44 123,test1,today
                +44456,    ,tomorrow
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
