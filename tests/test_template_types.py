import pytest
import mock
from flask import Markup
from freezegun import freeze_time

from notifications_utils.formatters import unlink_govuk_escaped, linkify
from notifications_utils.field import Field
from notifications_utils.template import (
    Template,
    HTMLEmailTemplate,
    LetterPreviewTemplate,
    LetterPDFLinkTemplate,
    PlainTextEmailTemplate,
    SMSMessageTemplate,
    SMSPreviewTemplate,
    WithSubjectTemplate,
    EmailPreviewTemplate,
)


def test_pass_through_renderer():
    message = '''
        the
        quick brown
        fox
    '''
    assert str(Template({'content': message})) == message


def test_html_email_inserts_body():
    assert 'the &lt;em&gt;quick&lt;/em&gt; brown fox' in str(HTMLEmailTemplate(
        {'content': 'the <em>quick</em> brown fox', 'subject': ''}
    ))


@pytest.mark.parametrize(
    "content", ('DOCTYPE', 'html', 'body', 'GOV.UK', 'hello world')
)
def test_default_template(content):
    assert content in str(HTMLEmailTemplate({'content': 'hello world', 'subject': ''}))


@pytest.mark.parametrize(
    "show_banner", (True, False)
)
def test_govuk_banner(show_banner):
    email = HTMLEmailTemplate({'content': 'hello world', 'subject': ''})
    email.govuk_banner = show_banner
    if show_banner:
        assert "GOV.UK" in str(email)
    else:
        assert "GOV.UK" not in str(email)


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

    email = str(HTMLEmailTemplate(
        {'content': 'hello world', 'subject': ''},
        complete_html=complete_html,
        brand_logo=brand_logo,
        brand_name=brand_name,
        brand_colour=brand_colour,
    ))

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


@pytest.mark.parametrize('template_class, result, markdown_renderer', [
    [
        HTMLEmailTemplate,
        (
            'the quick brown fox\n'
            '\n'
            'jumped over the lazy dog'
        ),
        'notifications_utils.template.notify_email_markdown',
    ],
    [
        LetterPreviewTemplate,
        (
            '# animal story\n'
            '\n'
            'the quick brown fox\n'
            '\n'
            'jumped over the lazy dog'
        ),
        'notifications_utils.template.notify_letter_preview_markdown'
    ]
])
def test_markdown_in_templates(
    template_class,
    result,
    markdown_renderer,
):
    with mock.patch(markdown_renderer) as mock_markdown_renderer:
        str(template_class(
            {
                "content": (
                    'the quick ((colour)) ((animal))\n'
                    '\n'
                    'jumped over the lazy dog'
                ),
                'subject': 'animal story'
            },
            {'animal': 'fox', 'colour': 'brown'}
        ))
    mock_markdown_renderer.assert_called_once_with(result)


@pytest.mark.parametrize(
    "url, url_with_entities_replaced", [
        ("http://example.com", "http://example.com"),
        ("http://www.gov.uk/", "http://www.gov.uk/"),
        ("https://www.gov.uk/", "https://www.gov.uk/"),
        ("http://service.gov.uk", "http://service.gov.uk"),
        (
            "http://service.gov.uk/blah.ext?q=a%20b%20c&order=desc#fragment",
            "http://service.gov.uk/blah.ext?q=a%20b%20c&amp;order=desc#fragment",
        ),
        pytest.mark.xfail(("example.com", "example.com")),
        pytest.mark.xfail(("www.example.com", "www.example.com")),
        pytest.mark.xfail((
            "http://service.gov.uk/blah.ext?q=one two three",
            "http://service.gov.uk/blah.ext?q=one two three",
        )),
        pytest.mark.xfail(("ftp://example.com", "ftp://example.com")),
        pytest.mark.xfail(("mailto:test@example.com", "mailto:test@example.com")),
    ]
)
def test_makes_links_out_of_URLs(url, url_with_entities_replaced):
    link = '<a style="word-wrap: break-word;" href="{}">{}</a>'.format(
        url_with_entities_replaced, url_with_entities_replaced
    )
    assert link in str(HTMLEmailTemplate({'content': url, 'subject': ''}))
    assert link in str(EmailPreviewTemplate({'content': url, 'subject': ''}))


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


@mock.patch('notifications_utils.template.add_prefix', return_value='')
@pytest.mark.parametrize(
    'template_class', [SMSMessageTemplate, SMSPreviewTemplate]
)
@pytest.mark.parametrize(
    "prefix, body, expected_call", [
        ("a", "b", (Markup("b"), "a")),
        (None, "b", (Markup("b"), None)),
    ]
)
def test_sms_message_adds_prefix(add_prefix, template_class, prefix, body, expected_call):
    template = template_class({'content': body})
    template.prefix = prefix
    template.sender = None
    str(template)
    add_prefix.assert_called_once_with(*expected_call)


@mock.patch('notifications_utils.template.add_prefix', return_value='')
@pytest.mark.parametrize(
    'template_class', [SMSMessageTemplate, SMSPreviewTemplate]
)
@pytest.mark.parametrize(
    "prefix, body, sender, expected_call", [
        ("a", "b", "c", (Markup("b"), None)),
        ("a", "b", None, (Markup("b"), "a")),
        ("a", "b", False, (Markup("b"), "a")),
    ]
)
def test_sms_message_adds_prefix_only_if_no_sender_set(add_prefix, prefix, body, sender, expected_call, template_class):
    template = template_class({'content': body}, prefix=prefix, sender=sender)
    str(template)
    add_prefix.assert_called_once_with(*expected_call)


@mock.patch('notifications_utils.template.nl2br')
def test_sms_preview_adds_newlines(nl2br):
    content = "the\nquick\n\nbrown fox"
    str(SMSPreviewTemplate({'content': content}))
    nl2br.assert_called_once_with(content)


@freeze_time("2001-01-01 12:00:00.000000")
@mock.patch('notifications_utils.template.LetterPreviewTemplate.jinja_template.render')
@mock.patch('notifications_utils.template.remove_empty_lines', return_value='123 Street')
@mock.patch('notifications_utils.template.unlink_govuk_escaped')
@mock.patch('notifications_utils.template.linkify')
@mock.patch('notifications_utils.template.notify_letter_preview_markdown', return_value='Bar')
@mock.patch('notifications_utils.template.prepare_newlines_for_markdown', return_value='Baz')
def test_letter_preview_renderer(
    prepare_newlines,
    letter_markdown,
    linkify,
    unlink_govuk,
    remove_empty_lines,
    jinja_template
):
    str(LetterPreviewTemplate({'content': 'Foo', 'subject': 'Subject', 'values': {}}))
    jinja_template.assert_called_once_with({
        'address': '123 Street',
        'message': 'Bar',
        'date': '1 January 2001'
    })
    prepare_newlines.assert_called_once_with('# Subject\n\nFoo')
    letter_markdown.assert_called_once_with('Baz')
    linkify.assert_not_called()
    unlink_govuk.assert_not_called()


@mock.patch('notifications_utils.template.LetterPDFLinkTemplate.jinja_template.render')
def test_letter_link_renderer(jinja_template):
    str(LetterPDFLinkTemplate(
        {'content': '', 'subject': ''},
        preview_url='http://example.com/endpoint'
    ))
    jinja_template.assert_called_once_with({
        'pdf_url': 'http://example.com/endpoint.pdf',
        'png_url': 'http://example.com/endpoint.png',
    })


def test_letter_link_renderer_requires_url():
    with pytest.raises(TypeError) as error:
        LetterPDFLinkTemplate({'content': '', 'subject': ''})


def test_sets_subject():
    assert WithSubjectTemplate({"content": '', 'subject': 'Your tax is due'}).subject == 'Your tax is due'


def test_subject_line_gets_applied_to_correct_template_types():
    for cls in [
        EmailPreviewTemplate,
        HTMLEmailTemplate,
        PlainTextEmailTemplate,
        LetterPreviewTemplate,
    ]:
        assert issubclass(cls, WithSubjectTemplate)
    for cls in [
        SMSMessageTemplate,
        SMSPreviewTemplate,
    ]:
        assert not issubclass(cls, WithSubjectTemplate)


def test_subject_line_gets_replaced():
    template = WithSubjectTemplate({"content": '', 'subject': '((name))'})
    assert template.subject == Markup("<span class='placeholder'>((name))</span>")
    template.values = {'name': 'Jo'}
    assert template.subject == 'Jo'


@pytest.mark.parametrize('template_class, extra_args, expected_field_calls', [
    (HTMLEmailTemplate, {}, [
        mock.call('bar', {}, html='escape')
    ]),
    (EmailPreviewTemplate, {}, [
        mock.call('bar', {}, html='escape'),
        mock.call('baz', {}, html='escape'),
        mock.call('((email address))', {}, with_brackets=False),
    ]),
    (SMSMessageTemplate, {}, [
        mock.call('bar', {}, html='passthrough'),
    ]),
    (SMSPreviewTemplate, {}, [
        mock.call('((phone number))', {}, with_brackets=False, html='escape'),
        mock.call('bar', {}, html='escape'),
    ]),
    (LetterPreviewTemplate, {}, [
        mock.call('bar', {}, html='escape'),
        mock.call('baz', {}, html='escape'),
        mock.call((
            '((address line 1))\n'
            '((address line 2))\n'
            '((address line 3))\n'
            '((address line 4))\n'
            '((address line 5))\n'
            '((address line 6))\n'
            '((postcode))'
        ), {}, with_brackets=False, html='escape'),
    ]),
    (LetterPDFLinkTemplate, {'preview_url': 'http://example.com'}, [
    ]),
])
@mock.patch('notifications_utils.template.Field.__init__', return_value=None)
@mock.patch('notifications_utils.template.Field.__str__', return_value='foo')
def test_templates_handle_html(
    mock_field_str,
    mock_field_init,
    template_class,
    extra_args,
    expected_field_calls,
):
    assert str(template_class({'content': 'bar', 'subject': 'baz'}, **extra_args))
    assert mock_field_init.call_args_list == expected_field_calls
