import pytest
from io import BytesIO

from utils.process_csv import get_rows_from_csv, get_recipients_from_csv


@pytest.mark.parametrize(
    "file_contents,expected",
    [
        (
            """
                phone number,name
                +44 123, test1
                +44 456,test2
            """,
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
            [
                {'email address': 'test@example.com', 'name': 'test1'},
                {'email address': 'test2@example.com', 'name': 'test2'}
            ]
        )
    ]
)
def test_get_rows(file_contents, expected):
    assert list(get_rows_from_csv(file_contents)) == expected


@pytest.mark.parametrize(
    "file_contents,template_type,expected",
    [
        (
            """
                phone number,name
                +44 123,test1
                +44 456,test2
            """,
            'sms',
            ['+44123', '+44456']
        ),
        (
            """
                email address,name
                test@example.com,test1
                test2@example.com,test2
            """,
            'email',
            ['test@example.com', 'test2@example.com']
        )
    ]
)
def test_get_recipients(file_contents, template_type, expected):
    assert list(get_recipients_from_csv(file_contents, template_type)) == expected
