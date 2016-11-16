import pytest
import mock
from notifications_utils.renderers import (
    PassThrough, HTMLEmail, PlainTextEmail, SMSMessage, SMSPreview, LetterPreview, unlink_govuk_escaped, linkify
)
from notifications_utils.field import Field


def test_pass_through_renderer():
    message = '''
        the
        quick brown
        fox
    '''
    assert PassThrough()(message) == message


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
    "branding_should_be_present, brand_logo, brand_name, brand_colour",
    [
        (True, 'http://example.com/image.png', 'Example', '#f00'),
        (True, 'http://example.com/image.png', 'Example', None),
        (True, 'http://example.com/image.png', '', None),
        (False, None, 'Example', '#f00'),
        (False, 'http://example.com/image.png', None, '#f00')
    ]
)
@pytest.mark.parametrize(
    "content", ('DOCTYPE', 'html', 'body')
)
def test_complete_html(complete_html, branding_should_be_present, brand_logo, brand_name, brand_colour, content):

    email = HTMLEmail(
        complete_html=complete_html,
        brand_logo=brand_logo,
        brand_name=brand_name,
        brand_colour=brand_colour
    )('hello world')

    if complete_html:
        assert content in email
    else:
        assert content not in email

    if branding_should_be_present:
        assert brand_logo in email
        assert brand_name in email

        if brand_colour:
            assert brand_colour in email
            assert '##' not in email


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
    link = '<a style="word-wrap: break-word;" href="{}">{}</a>'.format(url, url)
    assert (linkify(url) == link)
    assert link in HTMLEmail()(url)


@pytest.mark.parametrize(
    "url, expected_html", [
        (
            """https://example.com"onclick="alert('hi')""",
            """<a style="word-wrap: break-word;" href="https://example.com%22onclick=%22alert%28%27hi%27%29">https://example.com"onclick="alert('hi')</a>"""  # noqa
        ),
        (
            """https://example.com"style='text-decoration:blink'""",
            """<a style="word-wrap: break-word;" href="https://example.com%22style=%27text-decoration:blink%27">https://example.com"style='text-decoration:blink'</a>"""  # noqa
        ),
    ]
)
def test_URLs_get_escaped(url, expected_html):
    assert linkify(url) == expected_html
    assert expected_html in HTMLEmail()(url)


def test_HTML_template_has_URLs_replaced_with_links():
    assert (
        '<a style="word-wrap: break-word;" href="https://service.example.com/accept_invite/a1b2c3d4">'
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


@pytest.mark.parametrize(
    "prefix, body, sender, expected", [
        ("a", "b", "c", "b"),
        ("a", "b", None, "a: b"),
        ("a", "b", False, "a: b"),
    ]
)
def test_sms_message_adds_prefix_only_if_no_sender_set(prefix, body, sender, expected):
    assert SMSMessage(prefix=prefix, sender=sender)(body) == expected
    assert SMSPreview(prefix=prefix, sender=sender)(body) == expected


def test_sms_preview_adds_newlines():
    assert SMSPreview()("""
        the
        quick

        brown fox
    """) == "the<br>        quick<br><br>        brown fox"


@mock.patch('notifications_utils.renderers.unlink_govuk_escaped')
@mock.patch('notifications_utils.renderers.linkify')
@mock.patch('notifications_utils.renderers.notify_letter_preview_markdown', return_value='Bar')
@mock.patch('notifications_utils.renderers.prepare_newlines_for_markdown', return_value='Baz')
@mock.patch('notifications_utils.renderers.prepend_postal_address', return_value='Boo')
def test_letter_preview_renderer(prepend_postal, prepare_newlines, letter_markdown, linkify, unlink_govuk):
    assert LetterPreview(subject='Subject')('Foo') == 'Bar'
    assert prepend_postal.call_args[0][0] == '# Subject\n\nFoo'
    assert isinstance(prepend_postal.call_args[0][1], Field)
    prepare_newlines.assert_called_once_with('Boo')
    letter_markdown.assert_called_once_with('Baz')
    linkify.assert_not_called()
    unlink_govuk.assert_not_called()
