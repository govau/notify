import pytest
from notifications_utils.html_email import HTMLEmail


def test_html_email_inserts_body():
    assert 'the <em>quick</em> brown fox' in HTMLEmail()('the <em>quick</em> brown fox')


@pytest.mark.parametrize(
    "show_banner", (True, False)
)
def test_govuk_banner(show_banner):
    email = HTMLEmail(govuk_banner=show_banner)('hello world')
    if show_banner:
        assert "GOV.UK" in email
    else:
        assert "GOV.UK" not in email
