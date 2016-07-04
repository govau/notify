import pytest
from notifications_utils.html_email import HTMLEmail


def test_html_email_inserts_body():
    assert 'the <em>quick</em> brown fox' in HTMLEmail()('the <em>quick</em> brown fox')


@pytest.mark.parametrize(
    "content", ('DOCTYPE', 'html', 'body', 'GOV.UK', 'hello world')
)
def test_default_template(content):
    assert content in HTMLEmail()('hello world')


@pytest.mark.parametrize(
    "show_banner", (True, False)
)
def test_govuk_banner(show_banner):
    email = HTMLEmail(govuk_banner=show_banner)('hello world')
    if show_banner:
        assert "GOV.UK" in email
    else:
        assert "GOV.UK" not in email


@pytest.mark.parametrize(
    "complete_html", (True, False)
)
@pytest.mark.parametrize(
    "content", ('DOCTYPE', 'html', 'body')
)
def test_complete_html(complete_html, content):
    email = HTMLEmail(complete_html=complete_html)('hello world')
    if complete_html:
        assert content in email
    else:
        assert content not in email
