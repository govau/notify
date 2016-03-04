import pytest

from utils.recipients import RecipientCSV


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
    assert list(RecipientCSV(file_contents).rows) == expected


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
