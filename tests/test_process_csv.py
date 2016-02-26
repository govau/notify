import pytest
from io import BytesIO

from utils.process_csv import get_recipients_from_csv


@pytest.mark.parametrize(
    "file_contents,expected",
    [
        (
            'to,name\n+44 123,test1\n+44 456,test2',
            ['+44123', '+44456']
        )
    ]
)
def test_class(file_contents, expected):
    assert list(get_recipients_from_csv(file_contents)) == expected
