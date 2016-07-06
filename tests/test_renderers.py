import pytest
from notifications_utils.renderers import HTMLEmail


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


@pytest.mark.parametrize(
    "url", [
        "http://example.com",
        "http://www.gov.uk/",
        "https://www.gov.uk/",
        "http://service.gov.uk",
        "http://service.gov.uk/blah.ext?q=a%20b%20c&order=desc#fragment",
        pytest.mark.xfail("example.com"),
        pytest.mark.xfail("www.example.com"),
        pytest.mark.xfail("http://service.gov.uk/blah.ext?q=one two three"),
        pytest.mark.xfail("ftp://example.com"),
        pytest.mark.xfail("mailto:test@example.com")
    ]
)
def test_makes_links_out_of_URLs(url):
    assert (HTMLEmail.linkify(url) == '<a href="{}">{}</a>'.format(
        url, url
    ))


@pytest.mark.parametrize(
    "url, expected_html", [
        (
            """https://example.com"onclick="alert('hi')""",
            """<a href="https://example.com%22onclick=%22alert%28%27hi%27%29">https://example.com"onclick="alert('hi')</a>"""  # noqa
        ),
        (
            """https://example.com"style='text-decoration:blink'""",
            """<a href="https://example.com%22style=%27text-decoration:blink%27">https://example.com"style='text-decoration:blink'</a>"""  # noqa
        ),
    ]
)
def test_URLs_get_escaped(url, expected_html):
    assert HTMLEmail.linkify(url) == expected_html


def test_HTML_template_has_URLs_replaced_with_links():
    assert (
        '<a href="https://service.example.com/accept_invite/a1b2c3d4">'
        'https://service.example.com/accept_invite/a1b2c3d4'
        '</a>'
    ) in HTMLEmail()('''
        You’ve been invited to a service. Click this link:
        https://service.example.com/accept_invite/a1b2c3d4

        Thanks
    ''')


@pytest.mark.parametrize(
    "template_content,expected", [
        ("gov.uk", u"gov.\u200Buk"),
        ("GOV.UK", u"GOV.\u200BUK"),
        ("Gov.uk", u"Gov.\u200Buk"),
        ("https://gov.uk", "https://gov.uk"),
        ("https://www.gov.uk", "https://www.gov.uk"),
        ("www.gov.uk", "www.gov.uk"),
        ("gov.uk/register-to-vote", "gov.uk/register-to-vote"),
        ("gov.uk?q=", "gov.uk?q=")
    ]
)
def test_escaping_govuk_in_email_templates(template_content, expected):
    assert HTMLEmail.unlink_govuk_escaped(template_content) == expected
    assert expected in HTMLEmail()(template_content)
