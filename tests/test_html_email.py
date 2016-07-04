import pytest
from notifications_utils.html_email import HTMLEmail


def test_html_email_inserts_body():
    assert 'the <em>quick</em> brown fox' in HTMLEmail()('the <em>quick</em> brown fox')
