import pytest
from flask import Markup

from notifications_utils.formatters import (
    unlink_govuk_escaped,
    notify_email_markdown,
    notify_letter_preview_markdown,
    notify_letter_dvla_markdown,
    prepare_newlines_for_markdown,
    gsm_encode,
    formatted_list,
    strip_dvla_markup,
    strip_pipes,
    escape_html,
)
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
    assert (notify_email_markdown(url) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        '{}'
        '</p>'
    ).format(link))


@pytest.mark.parametrize('input, output', [
    (
        (
            'this is some text with a link http://example.com in the middle'
        ),
        (
            'this is some text with a link '
            '<a style="word-wrap: break-word;" href="http://example.com">http://example.com</a>'
            ' in the middle'
        ),
    ),
    (
        (
            'this link is in brackets (http://example.com)'
        ),
        (
            'this link is in brackets '
            '(<a style="word-wrap: break-word;" href="http://example.com">http://example.com</a>)'
        ),
    )
])
def test_makes_links_out_of_URLs_in_context(input, output):
    assert notify_email_markdown(input) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        '{}'
        '</p>'
    ).format(output)


@pytest.mark.parametrize(
    "url", [
        "example.com",
        "www.example.com",
        "ftp://example.com",
        "test@example.com",
        "mailto:test@example.com",
        "<a href=\"https://example.com\">Example</a>",
    ]
)
def test_doesnt_make_links_out_of_invalid_urls(url):
    assert notify_email_markdown(url) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        '{}'
        '</p>'
    ).format(url)


def test_handles_placeholders_in_urls():
    assert notify_email_markdown(
        "http://example.com/?token=<span class='placeholder'>((token))</span>&key=1"
    ) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        '<a style="word-wrap: break-word;" href="http://example.com/?token=">'
        'http://example.com/?token='
        '</a>'
        '<span class=\'placeholder\'>((token))</span>&amp;key=1'
        '</p>'
    )


@pytest.mark.parametrize(
    "url, expected_html", [
        (
            """https://example.com"onclick="alert('hi')""",
            """<a style="word-wrap: break-word;" href="https://example.com%22onclick=%22alert%28%27hi">https://example.com"onclick="alert('hi</a>')"""  # noqa
        ),
        (
            """https://example.com"style='text-decoration:blink'""",
            """<a style="word-wrap: break-word;" href="https://example.com%22style=%27text-decoration:blink">https://example.com"style='text-decoration:blink</a>'"""  # noqa
        ),
    ]
)
def test_URLs_get_escaped(url, expected_html):
    assert notify_email_markdown(url) == (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        '{}'
        '</p>'
    ).format(expected_html)
    assert expected_html in str(HTMLEmailTemplate({'content': url, 'subject': ''}))


def test_HTML_template_has_URLs_replaced_with_links():
    assert (
        '<a style="word-wrap: break-word;" href="https://service.example.com/accept_invite/a1b2c3d4">'
        'https://service.example.com/accept_invite/a1b2c3d4'
        '</a>'
    ) in str(HTMLEmailTemplate({'content': '''
        You’ve been invited to a service. Click this link:
        https://service.example.com/accept_invite/a1b2c3d4

        Thanks
    ''', 'subject': ''}))


def test_preserves_whitespace_when_making_links():
    assert (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        '<a style="word-wrap: break-word;" href="https://example.com">'
        'https://example.com'
        '</a>'
        '</p>'
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        'Next paragraph'
        '</p>'
    ) == notify_email_markdown(
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
    assert str(PlainTextEmailTemplate({'content': template_content, 'subject': ''})) == expected
    assert expected in str(HTMLEmailTemplate({'content': template_content, 'subject': ''}))


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


@pytest.mark.parametrize(
    'markdown_function, expected',
    (
        [
            notify_letter_preview_markdown,
            'print("hello")'
        ],
        [
            notify_letter_dvla_markdown,
            'print("hello")'
        ],
        [
            notify_email_markdown,
            'print("hello")'
        ]
    )
)
def test_block_code(markdown_function, expected):
    assert markdown_function('```\nprint("hello")\n```') == expected


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        (
            '<p>'
            'inset text'
            '</p>'
        )
    ],
    [
        notify_letter_dvla_markdown,
        (
            'inset text<cr><cr>'
        )
    ],
    [
        notify_email_markdown,
        (
            '<blockquote '
            'style="Margin: 0 0 20px 0; border-left: 10px solid #BFC1C3;'
            'padding: 15px 0 0.1px 15px; font-size: 19px; line-height: 25px;'
            '">'
            '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">inset text</p>'
            '</blockquote>'
        )
    ]
))
def test_block_quote(markdown_function, expected):
    assert markdown_function('^ inset text') == expected


@pytest.mark.parametrize(
    'markdown_function, expected',
    (
        [
            notify_letter_preview_markdown,
            '<h2>heading</h2>\n'
        ],
        [
            notify_letter_dvla_markdown,
            '<h2>heading<normal><cr><cr>'
        ],
        [
            notify_email_markdown,
            (
                '<h2 style="Margin: 0 0 20px 0; padding: 0; font-size: 27px; '
                'line-height: 35px; font-weight: bold; color: #0B0C0C;">'
                'heading'
                '</h2>'
            )
        ]
    )
)
def test_level_1_header(markdown_function, expected):
    assert markdown_function('# heading') == expected


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        '<p>inset text</p>'
    ],
    [
        notify_letter_dvla_markdown,
        'inset text<cr><cr>'
    ],
    [
        notify_email_markdown,
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">inset text</p>'
    ]
))
def test_level_2_header(markdown_function, expected):
    assert markdown_function('## inset text') == (expected)


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        (
            '<p>a</p>'
            '<p>b</p>'
        )
    ],
    [
        notify_letter_dvla_markdown,
        (
            'a<cr><cr>'
            'b<cr><cr>'
        )
    ],
    [
        notify_email_markdown,
        (
            '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">a</p>'
            '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">b</p>'
        )
    ]
))
def test_hrule(markdown_function, expected):
    assert markdown_function('a\n\n***\n\nb') == expected
    assert markdown_function('a\n\n---\n\nb') == expected


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        (
            '<ol>\n'
            '<li>one</li>\n'
            '<li>two</li>\n'
            '<li>three</li>\n'
            '</ol>\n'
        )
    ],
    [
        notify_letter_dvla_markdown,
        (
            '<np>one'
            '<np>two'
            '<np>three'
            '<p><cr>'
        )
    ],
    [
        notify_email_markdown,
        (
            '<ol style="Margin: 0 0 20px 0; padding: 0; list-style-type: decimal;">'
            '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
            'line-height: 25px; color: #0B0C0C;">one</li>'
            '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
            'line-height: 25px; color: #0B0C0C;">two</li>'
            '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
            'line-height: 25px; color: #0B0C0C;">three</li>'
            '</ol>'
        )
    ]
))
def test_ordered_list(markdown_function, expected):
    assert markdown_function(
        '1. one\n'
        '2. two\n'
        '3. three\n'
    ) == expected


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        (
            '<ul>\n'
            '<li>one</li>\n'
            '<li>two</li>\n'
            '<li>three</li>\n'
            '</ul>\n'
        )
    ],
    [
        notify_letter_dvla_markdown,
        (
            '<cr>'
            '<op><bul><tab>one'
            '<op><bul><tab>two'
            '<op><bul><tab>three'
            '<p><cr>'
        )
    ],
    [
        notify_email_markdown,
        (
            '<ul style="Margin: 0 0 20px 0; padding: 0; list-style-type: disc;">'
            '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
            'line-height: 25px; color: #0B0C0C;">one</li>'
            '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
            'line-height: 25px; color: #0B0C0C;">two</li>'
            '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
            'line-height: 25px; color: #0B0C0C;">three</li>'
            '</ul>'
        )
    ]
))
def test_unordered_list(markdown_function, expected):
    assert markdown_function(
        '* one\n'
        '* two\n'
        '* three\n'
    ) == expected


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        (
            '<p>line one<br/>'
            'line two</p>'
            '<p>new paragraph</p>'
        )
    ],
    [
        notify_letter_dvla_markdown,
        (
            'line one<cr>'
            'line two<cr><cr>'
            'new paragraph<cr><cr>'
        )
    ],
    [
        notify_email_markdown,
        (
            '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">line one<br/>'
            'line two</p>'
            '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">new paragraph</p>'
        )
    ]
))
def test_paragraphs(markdown_function, expected):
    assert markdown_function(
        'line one\n'
        'line two\n'
        '\n'
        'new paragraph'
    ) == expected


@pytest.mark.parametrize('markdown_function', (
    notify_letter_preview_markdown, notify_letter_dvla_markdown, notify_email_markdown
))
def test_table(markdown_function):
    assert markdown_function(
        'col | col\n'
        '----|----\n'
        'val | val\n'
    ) == (
        ''
    )


@pytest.mark.parametrize('markdown_function, link, expected', (
    [
        notify_letter_preview_markdown,
        'http://example.com',
        '<p><strong>example.com</strong></p>'
    ],
    [
        notify_letter_dvla_markdown,
        'http://example.com',
        '<b>example.com<normal><cr><cr>'
    ],
    [
        notify_email_markdown,
        'http://example.com',
        (
            '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
            '<a style="word-wrap: break-word;" href="http://example.com">http://example.com</a>'
            '</p>'
        )
    ],
    [
        notify_email_markdown,
        """https://example.com"onclick="alert('hi')""",
        (
            '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
            '<a style="word-wrap: break-word;" href="https://example.com%22onclick=%22alert%28%27hi">'
            'https://example.com"onclick="alert(\'hi'
            '</a>\')'
            '</p>'
        )
    ]
))
def test_autolink(markdown_function, link, expected):
    assert markdown_function(link) == expected


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        '<p>variable called thing</p>'
    ],
    [
        notify_letter_dvla_markdown,
        'variable called thing<cr><cr>'
    ],
    [
        notify_email_markdown,
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">variable called thing</p>'
    ]
))
def test_codespan(markdown_function, expected):
    assert markdown_function(
        'variable called `thing`'
    ) == expected


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        '<p>something important</p>'
    ],
    [
        notify_letter_dvla_markdown,
        'something important<cr><cr>'
    ],
    [
        notify_email_markdown,
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">something important</p>'
    ]
))
def test_double_emphasis(markdown_function, expected):
    assert markdown_function(
        'something **important**'
    ) == expected


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        '<p>something important</p>'
    ],
    [
        notify_letter_dvla_markdown,
        'something important<cr><cr>'
    ],
    [
        notify_email_markdown,
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">something important</p>'
    ]
))
def test_emphasis(markdown_function, expected):
    assert markdown_function(
        'something *important*'
    ) == expected


@pytest.mark.parametrize('markdown_function', (
    notify_letter_preview_markdown, notify_letter_dvla_markdown, notify_email_markdown
))
def test_image(markdown_function):
    assert markdown_function(
        '![alt text](http://example.com/image.png)'
    ) == (
        ''
    )


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        (
            '<p>Example: <strong>example.com</strong></p>'
        )
    ],
    [
        notify_letter_dvla_markdown,
        (
            'Example: <b>example.com<normal><cr><cr>'
        )
    ],
    [
        notify_email_markdown,
        (
            '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; '
            'color: #0B0C0C;">'
            'Example: <a style="word-wrap: break-word;" href="http://example.com">http://example.com</a>'
            '</p>'
        )
    ]
))
def test_link(markdown_function, expected):
    assert markdown_function(
        '[Example](http://example.com)'
    ) == expected


@pytest.mark.parametrize('markdown_function, expected', (
    [
        notify_letter_preview_markdown,
        '<p>Strike</p>'
    ],
    [
        notify_letter_dvla_markdown,
        'Strike<cr><cr>'
    ],
    [
        notify_email_markdown,
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">Strike</p>'
    ]
))
def test_strikethrough(markdown_function, expected):
    assert markdown_function('~~Strike~~') == expected


def test_footnotes():
    # Can’t work out how to test this
    pass


def test_gsm_encode():
    assert gsm_encode('aàá…') == 'aàa...'


@pytest.mark.parametrize('items, kwargs, expected_output', [
    ([1], {}, '‘1’'),
    ([1, 2], {}, '‘1’ and ‘2’'),
    ([1, 2, 3], {}, '‘1’, ‘2’ and ‘3’'),
    ([1, 2, 3], {'prefix': 'foo', 'prefix_plural': 'bar'}, 'bar ‘1’, ‘2’ and ‘3’'),
    ([1], {'prefix': 'foo', 'prefix_plural': 'bar'}, 'foo ‘1’'),
    ([1, 2, 3], {'before_each': 'a', 'after_each': 'b'}, 'a1b, a2b and a3b'),
    ([1, 2, 3], {'conjunction': 'foo'}, '‘1’, ‘2’ foo ‘3’'),
    (['&'], {'before_each': '<i>', 'after_each': '</i>'}, '<i>&amp;</i>'),
    ([1, 2, 3], {'before_each': '<i>', 'after_each': '</i>'}, '<i>1</i>, <i>2</i> and <i>3</i>'),
])
def test_formatted_list(items, kwargs, expected_output):
    assert formatted_list(items, **kwargs) == expected_output


def test_formatted_list_returns_markup():
    assert isinstance(formatted_list([0]), Markup)


def test_removing_dvla_markup():
    assert strip_dvla_markup(
        (
            'some words & some more <words>'
            '<cr><h1><h2><p><normal><op><np><bul><tab>'
            '<CR><H1><H2><P><NORMAL><OP><NP><BUL><TAB>'
            '<tAb>'
        )
    ) == 'some words & some more <words>'


def test_removing_pipes():
    assert strip_pipes('|a|b|c') == 'abc'


def test_bleach_doesnt_try_to_make_valid_html_before_cleaning():
    assert escape_html(
        "<to cancel daily cat facts reply 'cancel'>"
    ) == (
        "&lt;to cancel daily cat facts reply 'cancel'&gt;"
    )
