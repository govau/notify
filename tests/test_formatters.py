import pytest
from notifications_utils.formatters import (
    unlink_govuk_escaped,
    linkify,
    notify_email_markdown,
    notify_letter_preview_markdown,
    prepare_newlines_for_markdown,
)
from notifications_utils.field import Field
from notifications_utils.template import (
    HTMLEmailTemplate,
    PlainTextEmailTemplate,
    SMSMessageTemplate,
    SMSPreviewTemplate
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
    link = '<a style="word-wrap: break-word;" href="{}">{}</a>'.format(url, url)
    assert (linkify(url) == link)
    assert link in str(HTMLEmailTemplate({'content': url}))


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
    assert expected_html in str(HTMLEmailTemplate({'content': url}))


def test_HTML_template_has_URLs_replaced_with_links():
    assert (
        '<a style="word-wrap: break-word;" href="https://service.example.com/accept_invite/a1b2c3d4">'
        'https://service.example.com/accept_invite/a1b2c3d4'
        '</a>'
    ) in str(HTMLEmailTemplate({'content': '''
        You’ve been invited to a service. Click this link:
        https://service.example.com/accept_invite/a1b2c3d4

        Thanks
    '''}))


def test_preserves_whitespace_when_making_links():
    assert (
        '<a style="word-wrap: break-word;" href="https://example.com">'
        'https://example.com'
        '</a>\n'
        '\n'
        'Next paragraph'
    ) == linkify(
        'https://example.com\n'
        '\n'
        'Next paragraph'
    )


def test_add_spaces_after_single_newlines_so_markdown_converts_them():
    converted = prepare_newlines_for_markdown(
        'Paragraph one\n'
        '\n'
        'Paragraph two has linebreaks\n'
        'This is the second line\n'
        'The third has 2 spaces after it  \n'
        'And this is the fourth\n'
        '\n'
        'Next paragraph'
    )
    assert converted == (
        'Paragraph one\n'
        '\n'
        'Paragraph two has linebreaks  \n'
        'This is the second line  \n'
        'The third has 2 spaces after it  \n'
        'And this is the fourth\n'
        '\n'
        'Next paragraph'
    )
    assert notify_email_markdown(converted) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        'Paragraph one'
        '</p>'
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        'Paragraph two has linebreaks<br/>'
        'This is the second line<br/>'
        'The third has 2 spaces after it<br/>'
        'And this is the fourth'
        '</p>'
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        'Next paragraph'
        '</p>'
    )


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
    assert str(PlainTextEmailTemplate({'content': template_content})) == expected
    assert expected in str(HTMLEmailTemplate({'content': template_content}))


@pytest.mark.parametrize(
    "prefix, body, expected", [
        ("a", "b", "a: b"),
        (None, "b", "b"),
    ]
)
def test_sms_message_adds_prefix(prefix, body, expected):
    template = SMSMessageTemplate({'content': body})
    template.prefix = prefix
    template.sender = None
    assert str(template) == expected


def test_sms_preview_adds_newlines():
    template = SMSPreviewTemplate({'content': """
        the
        quick

        brown fox
    """})
    template.prefix = None
    template.sender = None
    assert '<br>' in str(template)


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_block_code(markdown_function):
    assert markdown_function('```\nprint("hello")\n```') == 'print("hello")'


def test_block_quote():
    assert notify_letter_preview_markdown('^ inset text') == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        'inset text'
        '</p>'
    )
    assert notify_email_markdown('^ inset text') == (
        '<blockquote '
        'style="Margin: 0 0 20px 0; border-left: 10px solid #BFC1C3;'
        'padding: 15px 0 0.1px 15px; font-size: 19px; line-height: 25px;'
        '">'
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">inset text</p>'
        '</blockquote>'
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_level_1_header(markdown_function):
    assert markdown_function('# heading') == (
        '<h2 style="Margin: 0 0 20px 0; padding: 0; font-size: 27px; '
        'line-height: 35px; font-weight: bold; color: #0B0C0C;">'
        'heading'
        '</h2>'
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_level_2_header(markdown_function):
    assert markdown_function(
        '## inset text'
    ) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">inset text</p>'
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_hrule(markdown_function):
    assert markdown_function('a\n\n***\n\nb') == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">a</p>'
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">b</p>'
    )
    assert markdown_function('a\n\n---\n\nb') == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">a</p>'
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">b</p>'
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_ordered_list(markdown_function):
    assert markdown_function(
        '1. one\n'
        '2. two\n'
        '3. three\n'
    ) == (
        '<ol style="Margin: 0 0 20px 0; padding: 0; list-style-type: decimal;">'
        '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
        'line-height: 25px; color: #0B0C0C;">one</li>'
        '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
        'line-height: 25px; color: #0B0C0C;">two</li>'
        '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
        'line-height: 25px; color: #0B0C0C;">three</li>'
        '</ol>'
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_unordered_list(markdown_function):
    assert markdown_function(
        '* one\n'
        '* two\n'
        '* three\n'
    ) == (
        '<ul style="Margin: 0 0 20px 0; padding: 0; list-style-type: disc;">'
        '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
        'line-height: 25px; color: #0B0C0C;">one</li>'
        '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
        'line-height: 25px; color: #0B0C0C;">two</li>'
        '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
        'line-height: 25px; color: #0B0C0C;">three</li>'
        '</ul>'
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_paragraphs(markdown_function):
    assert markdown_function(
        'line one\n'
        'line two\n'
        '\n'
        'new paragraph'
    ) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">line one\n'
        'line two</p>'
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">new paragraph</p>'
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_table(markdown_function):
    assert markdown_function(
        'col | col\n'
        '----|----\n'
        'val | val\n'
    ) == (
        ''
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_autolink(markdown_function):
    assert markdown_function(
        'http://example.com'
    ) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">http://example.com</p>'  # noqa
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_codespan(markdown_function):
    assert markdown_function(
        'variable called `thing`'
    ) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; '
        'color: #0B0C0C;">variable called thing</p>'
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_double_emphasis(markdown_function):
    assert markdown_function(
        'something **important**'
    ) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">something important</p>'  # noqa
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_emphasis(markdown_function):
    assert markdown_function(
        'something *important*'
    ) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">something important</p>'  # noqa
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_image(markdown_function):
    assert markdown_function(
        '![alt text](http://example.com/image.png)'
    ) == (
        ''
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_link(markdown_function):
    assert markdown_function(
        '[Example](http://example.com)'
    ) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; '
        'color: #0B0C0C;">Example: http://example.com</p>'
    )


@pytest.mark.parametrize('markdown_function', (notify_letter_preview_markdown, notify_email_markdown))
def test_strikethrough(markdown_function):
    assert markdown_function(
        '~~Strike~~'
    ) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">Strike</p>'
    )


def test_footnotes():
    # Can’t work out how to test this
    pass
