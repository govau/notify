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
    "file_contents,template_type,expected_recipients,expected_personalisation",
    [
        (
            """
                phone number,name, date
                +44 123,test1,today
                +44456,    ,tomorrow
            """,
            'sms',
            ['+44 123', '+44456'],
            [{'name': 'test1', 'date': 'today'}, {'name': '', 'date': 'tomorrow'}]
        ),
        (
            """
                email address,name,colour
                test@example.com,test1,red
                testatexampledotcom,test2,blue
            """,
            'email',
            ['test@example.com', 'testatexampledotcom'],
            [
                {'name': 'test1', 'colour': 'red'},
                {'name': 'test2', 'colour': 'blue'}
            ]
        )
    ]
)
def test_get_recipient(file_contents, template_type, expected_recipients, expected_personalisation):
    recipients = RecipientCSV(file_contents, template_type=template_type)
    assert list(recipients.recipients) == expected_recipients
    assert list(recipients.personalisation) == expected_personalisation
    assert list(recipients.recipients_and_personalisation) == [
        (recipient, personalisation)
        for recipient, personalisation in zip(expected_recipients, expected_personalisation)
    ]


@pytest.mark.parametrize(
    "file_contents,template_type,expected,expected_highlighted",
    [
        (
            "", 'sms', [], []
        ),
        (
            """
                phone number,name
                +44 123,test1
                +44 123,test1
                +44 123,test1
            """,
            'sms',
            ['phone number', 'name'],
            ['phone number', Markup('<span class=\'placeholder\'>name</span>')]
        ),
        (
            """
                email address,name,colour
            """,
            'email',
            ['email address', 'name', 'colour'],
            ['email address', Markup('<span class=\'placeholder\'>name</span>'), 'colour']
        )
    ]
)
def test_column_headers(file_contents, template_type, expected, expected_highlighted):
    assert RecipientCSV(file_contents, template_type=template_type).column_headers == expected
    assert RecipientCSV(
        file_contents, template_type=template_type, placeholders=['name']
    ).column_headers_with_placeholders_highlighted == expected_highlighted
