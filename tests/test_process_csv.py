import pytest
from io import BytesIO

from utils.process_csv import get_rows_from_csv, get_recipient_from_row, get_personalisation_from_row


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
    "file_contents,template_type,expected_recipient,expected_personalisation",
    [
        (
            """
                phone number,name
                +44 123,test1
            """,
            'sms',
            '+44123',
            {'name': 'test1'}
        ),
        (
            """
                email address,name,colour
                test@example.com,test1,red
            """,
            'email',
            'test@example.com',
            {'name': 'test1', 'colour': 'red'}
        )
    ]
)
def test_get_recipient(file_contents, template_type, expected_recipient, expected_personalisation):
    csv = list(get_rows_from_csv(file_contents))
    assert get_recipient_from_row(csv[0], template_type) == expected_recipient
    assert get_personalisation_from_row(csv[0], template_type) == expected_personalisation
