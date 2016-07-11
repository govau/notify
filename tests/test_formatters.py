import pytest
from notifications_utils.renderers import (
    PassThrough, HTMLEmail, PlainTextEmail, SMSMessage, SMSPreview
)
from notifications_utils.formatters import (
    unlink_govuk_escaped, linkify, markup_headings, markup_lists, markup_blockquotes
)


@pytest.mark.parametrize(
    "url", [
        "http://example.com",
        "http://www.gov.uk/",
        "https://www.gov.uk/",
        "http://service.gov.uk",
        "http://service.gov.uk/blah.ext?q=a%20b%20c&order=desc#fragment",
        pytest.mark.xfail("http://service.gov.uk/blah.ext?q=one two three"),
    ]
)
def test_makes_links_out_of_URLs(url):
    link = '<a href="{}">{}</a>'.format(url, url)
    assert (linkify(url) == link)
    assert link in HTMLEmail()(url)


@pytest.mark.parametrize(
    "url", [
        "example.com",
        "www.example.com",
        "ftp://example.com",
        "mailto:test@example.com",
        "http://service.gov.uk/register/<span class='placeholder'>((token))</span>"
    ]
)
def test_doesnt_make_links_out_of_invalid_urls(url):
    assert url == linkify(url)


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
    assert linkify(url) == expected_html
    assert expected_html in HTMLEmail()(url)


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
    assert unlink_govuk_escaped(template_content) == expected
    assert PlainTextEmail()(template_content) == expected
    assert expected in HTMLEmail()(template_content)


@pytest.mark.parametrize(
    "prefix, body, expected", [
        ("a", "b", "a: b"),
        (None, "b", "b"),
    ]
)
def test_sms_message_adds_prefix(prefix, body, expected):
    assert SMSMessage(prefix=prefix)(body) == expected
    assert SMSPreview(prefix=prefix)(body) == expected


def test_sms_preview_adds_newlines():
    assert SMSPreview()("""
        the
        quick

        brown fox
    """) == "the<br>        quick<br><br>        brown fox"


@pytest.mark.parametrize(
    "message, expected_html", [
        (
            '''
# This is a heading

And this is some text
            ''',
            '''
<h2 style="margin: 10px 0 0 0; padding: 0; font-size: 27px; font-weight: bold">This is a heading</h2>
And this is some text
            '''
        ),
    ]
)
def test_markup_headings(message, expected_html):
    assert expected_html == markup_headings(message)


@pytest.mark.parametrize(
    "message, expected_html", [
        (
            '''
* item 1
* item 2
* item 3
            ''',
            (
                '\n<li style="margin: 5px 0; display: list-item; list-style-type: disc; font-size: 19px;">item 1</li>'
                '<li style="margin: 5px 0; display: list-item; list-style-type: disc; font-size: 19px;">item 2</li>'
                '<li style="margin: 5px 0; display: list-item; list-style-type: disc; font-size: 19px;">item 3</li>'
                '            '
            )
        ),
    ]
)
def test_markup_lists(message, expected_html):
    assert expected_html == markup_lists(message)


@pytest.mark.parametrize(
    "message, expected_html", [
        (
            '''
^ some text
            ''',
            (
                '\n'
                '<blockquote style="margin: 0; border-left: 10px solid #BFC1C3; padding: 0 0 0 15px; font-size: 19px;">'
                'some text'
                '</blockquote>            '
            )
        ),
    ]
)
def test_markup_blockquotes(message, expected_html):
    assert expected_html == markup_blockquotes(message)
