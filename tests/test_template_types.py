import pytest
import mock
from flask import Markup
from freezegun import freeze_time

from notifications_utils.formatters import unlink_govuk_escaped
from notifications_utils.field import Field
from notifications_utils.template import (
    Template,
    HTMLEmailTemplate,
    LetterPreviewTemplate,
    LetterPDFLinkTemplate,
    LetterDVLATemplate,
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


@pytest.mark.parametrize('template_class, extra_args, result, markdown_renderer', [
    [
        HTMLEmailTemplate,
        {},
        (
            'the quick brown fox\n'
            '\n'
            'jumped over the lazy dog'
        ),
        'notifications_utils.template.notify_email_markdown',
    ],
    [
        LetterPreviewTemplate,
        {},
        (
            'the quick brown fox\n'
            '\n'
            'jumped over the lazy dog'
        ),
        'notifications_utils.template.notify_letter_preview_markdown'
    ],
    [
        LetterDVLATemplate,
        {'numeric_id': 1},
        (
            'the quick brown fox\n'
            '\n'
            'jumped over the lazy dog'
        ),
        'notifications_utils.template.notify_letter_dvla_markdown'
    ]
])
def test_markdown_in_templates(
    template_class,
    extra_args,
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
            {'animal': 'fox', 'colour': 'brown'},
            **extra_args
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
    "template_class, prefix, body, expected_call", [
        (SMSMessageTemplate, "a", "b", (Markup("b"), "a")),
        (SMSPreviewTemplate, "a", "b", (Markup("b"), "a")),
        (SMSMessageTemplate, None, "b", (Markup("b"), None)),
        (SMSPreviewTemplate, None, "b", (Markup("b"), None)),
        (SMSMessageTemplate, '<em>ht&ml</em>', "b", (Markup("b"), '<em>ht&ml</em>')),
        (SMSPreviewTemplate, '<em>ht&ml</em>', "b", (Markup("b"), '&lt;em&gt;ht&amp;ml&lt;/em&gt;')),
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


@mock.patch('notifications_utils.template.gsm_encode', return_value='downgraded')
@pytest.mark.parametrize(
    'template_class', [SMSMessageTemplate, SMSPreviewTemplate]
)
def test_sms_messages_downgrade_non_gsm(mock_gsm_encode, template_class):
    template = str(template_class({'content': 'Message'}, prefix='Service name'))
    assert 'downgraded' in str(template)
    mock_gsm_encode.assert_called_once_with('Service name: Message')


@mock.patch('notifications_utils.template.nl2br')
def test_sms_preview_adds_newlines(nl2br):
    content = "the\nquick\n\nbrown fox"
    str(SMSPreviewTemplate({'content': content}))
    nl2br.assert_called_once_with(content)


@freeze_time("2001-01-01 12:00:00.000000")
@mock.patch('notifications_utils.template.LetterPreviewTemplate.jinja_template.render')
@mock.patch('notifications_utils.template.remove_empty_lines', return_value='123 Street')
@mock.patch('notifications_utils.template.unlink_govuk_escaped')
@mock.patch('notifications_utils.template.notify_letter_preview_markdown', return_value='Bar')
@mock.patch('notifications_utils.template.prepare_newlines_for_markdown', return_value='Baz')
@pytest.mark.parametrize('values, expected_address', [
    ({}, Markup(
        "<span class='placeholder-no-brackets'>address line 1</span>\n"
        "<span class='placeholder-no-brackets'>address line 2</span>\n"
        "<span class='placeholder-no-brackets'>address line 3</span>\n"
        "<span class='placeholder-no-brackets'>address line 4</span>\n"
        "<span class='placeholder-no-brackets'>address line 5</span>\n"
        "<span class='placeholder-no-brackets'>address line 6</span>\n"
        "<span class='placeholder-no-brackets'>postcode</span>"
    )),
    ({
        'address line 1': '123 Fake Street',
        'address line 6': 'United Kingdom',
    }, Markup(
        "123 Fake Street\n"
        "<span class='placeholder-no-brackets'>address line 2</span>\n"
        "<span class='placeholder-no-brackets'>address line 3</span>\n"
        "<span class='placeholder-no-brackets'>address line 4</span>\n"
        "<span class='placeholder-no-brackets'>address line 5</span>\n"
        "United Kingdom\n"
        "<span class='placeholder-no-brackets'>postcode</span>"
    )),
    ({
        'address line 1': '123 Fake Street',
        'address line 2': 'City of Town',
        'postcode': 'SW1A 1AA',
    }, Markup(
        "123 Fake Street\n"
        "City of Town\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "SW1A 1AA"
    ))
])
@pytest.mark.parametrize('contact_block, expected_rendered_contact_block', [
    (
        None,
        ''
    ),
    (
        '',
        ''
    ),
])
def test_letter_preview_renderer(
    prepare_newlines,
    letter_markdown,
    unlink_govuk,
    remove_empty_lines,
    jinja_template,
    values,
    expected_address,
    contact_block,
    expected_rendered_contact_block,
):
    str(LetterPreviewTemplate(
        {'content': 'Foo', 'subject': 'Subject'},
        values,
        contact_block=contact_block,
    ))
    remove_empty_lines.assert_called_once_with(expected_address)
    jinja_template.assert_called_once_with({
        'address': '123 Street',
        'subject': 'Subject',
        'message': 'Bar',
        'date': '1 January 2001',
        'contact_block': expected_rendered_contact_block,
    })
    prepare_newlines.assert_called_once_with('Foo')
    letter_markdown.assert_called_once_with('Baz')
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
        LetterPDFLinkTemplate,
        LetterDVLATemplate,
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
        mock.call('content', {}, html='escape')
    ]),
    (EmailPreviewTemplate, {}, [
        mock.call('content', {}, html='escape'),
        mock.call('subject', {}, html='escape'),
        mock.call('((email address))', {}, with_brackets=False),
    ]),
    (SMSMessageTemplate, {}, [
        mock.call('content', {}, html='passthrough'),
    ]),
    (SMSPreviewTemplate, {}, [
        mock.call('((phone number))', {}, with_brackets=False, html='escape'),
        mock.call('content', {}, html='escape'),
    ]),
    (LetterPreviewTemplate, {}, [
        mock.call('subject', {}, html='escape'),
        mock.call('content', {}, html='escape'),
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
    assert str(template_class({'content': 'content', 'subject': 'subject'}, **extra_args))
    assert mock_field_init.call_args_list == expected_field_calls


def test_email_preview_escapes_html_in_from_name():
    template = EmailPreviewTemplate(
        {'content': 'content', 'subject': 'subject'},
        from_name='<script>alert("")</script>',
        from_address='test@example.com',
    )
    assert '<script>' not in str(template)
    assert '&lt;script&gt;alert("")&lt;/script&gt;' in str(template)


dvla_file_spec = [
    {
        'Field number': '1',
        'Field name': 'OTT',
        'Mandatory': 'Y',
        'Data type': 'N3',
        'Comment': """
            Current assumption is a single OTT for Notify = 140
            141 has also been reserved for future use
        """,
        'Example': '140',
    },
    {
        'Field number': '2',
        'Field name': 'ORG-ID',
        'Mandatory': 'Y',
        'Data type': 'N3',
        'Comment': 'Unique identifier for the sending organisation',
        'Example': '001',
    },
    {
        'Field number': '3',
        'Field name': 'ORG-NOTIFICATION-TYPE',
        'Mandatory': 'Y',
        'Data type': 'N3',
        'Comment': """
            Identifies the specific letter type for this organisation
        """,
        'Example': '001',
    },
    {
        'Field number': '4',
        'Field name': 'ORG-NAME',
        'Mandatory': 'Y',
        'Data type': 'A90',
        'Comment': """
            Free text organisation name which appears under the
            crest in large font

            Not used by Notify
        """,
        'Example': '',
    },
    {
        'Field number': '5',
        'Field name': 'NOTIFICATION-ID',
        'Mandatory': 'Y',
        'Data type': 'A15',
        'Comment': """
            Unique identifier for each notification consisting of
            the current date and a numeric counter that resets each
            day.  Supports a maximum of 10 million notification
            events per day. Format:
                CCYYMMDDNNNNNNN
            Where:
                CCYY = Current year
                MMDD = Current month and year (zero padded)
                NNNNNNN = Daily counter (zero padded to 7 digits)
        """,
        'Example': '201604290000001',
    },
    {
        'Field number': '6',
        'Field name': 'NOTIFICATION-DATE',
        'Mandatory': 'Y',
        'Data type': 'A8',
        'Comment': """
            The date that will be shown on the notification Provided
            in format': 'DDMMYYYY This will be formatted to a long
            date format by the composition process
        """,
        'Example': '29042016',
    },
    {
        'Field number': '7',
        'Field name': 'CUSTOMER-REFERENCE',
        'Mandatory': '',
        'Data type': 'A30',
        'Comment': """
            Full text of customer\'s reference

            Not implemented by Notify yet.

            Given example was:
                Our ref: 1234-5678
        """,
        'Example': '',
    },
    {
        'Field number': '8',
        'Field name': 'ADDITIONAL-LINE-1',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': """
            In the example templates this information appears in the
            footer in a small font.   These lines are free text,
            they may contain an address, e.g. of originating
            department, E9 but this will not be validated or used as
            a return address.

            Not used by Notify

            Given example was:
                The Pension Service
        """,
        'Example': '',
    },
    {
        'Field number': '9',
        'Field name': 'ADDITIONAL-LINE-2',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': """
            Not used by Notify

            Given example was:
                Mail Handling Site A
        """,
        'Example': '',
    },
    {
        'Field number': '10',
        'Field name': 'ADDITIONAL-LINE-3',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': """
            Not used by Notify.

            Given example was:
                Wolverhampton  WV9 1LU
        """,
        'Example': '',
    },
    {
        'Field number': '11',
        'Field name': 'ADDITIONAL-LINE-4',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': """
            Not used by Notify.

            Given example was:
                Telephone: 0845 300 0168
        """,
        'Example': '',
    },
    {
        'Field number': '12',
        'Field name': 'ADDITIONAL-LINE-5',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': """
            Not used by Notify.

            Given example was:
                Norfolk
        """,
        'Example': '',
    },
    {
        'Field number': '13',
        'Field name': 'ADDITIONAL-LINE-6',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': """
            Not used by Notify.

            Given example was:
                Email: fpc.customercare@dwp.gsi.gov.uk
        """,
        'Example': '',
    },
    {
        'Field number': '14',
        'Field name': 'ADDITIONAL-LINE-7',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': """
            Not used by Notify.

            Given example was:
                Monday - Friday  8am - 6pm
        """,
        'Example': '',
    },
    {
        'Field number': '15',
        'Field name': 'ADDITIONAL-LINE-8',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': """
            Not used by Notify.

            Given example was:
                www.gov.uk
        """,
        'Example': '',
    },
    {
        'Field number': '16',
        'Field name': 'ADDITIONAL-LINE-9',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': '',
        'Example': '',
    },
    {
        'Field number': '17',
        'Field name': 'ADDITIONAL-LINE-10',
        'Mandatory': '',
        'Data type': 'A50',
        'Comment': '',
        'Example': '',
    },
    {
        'Field number': '18',
        'Field name': 'TO-NAME-1',
        'Mandatory': 'Y',
        'Data type': 'A60',
        'Comment': """
            Recipient full name includes title Must be present -
            validated by Notify
        """,
        'Example': 'Mr Henry Hadlow',
    },
    {
        'Field number': '19',
        'Field name': 'TO-NAME-2',
        'Mandatory': '',
        'Data type': 'A40',
        'Comment': 'Additional name or title line',
        'Example': 'Managing Director',
    },
    {
        'Field number': '20',
        'Field name': 'TO-ADDRESS-LINE-1',
        'Mandatory': 'Y',
        'Data type': 'A35',
        'Comment': """
            Must be present - PAF validation by Notify Must match
            PAF (in combination with TO-POST-CODE) to maximise
            postage discount
        """,
        'Example': '123 Electric Avenue',
    },
    {
        'Field number': '21',
        'Field name': 'TO-ADDRESS-LINE-2',
        'Mandatory': '',
        'Data type': 'A35',
        'Comment': """
            Address lines 2 through 5 are optional Composition
            process will remove blank address lines
        """,
        'Example': 'Great Yarmouth',
    },
    {
        'Field number': '22',
        'Field name': 'TO-ADDRESS-LINE-3',
        'Mandatory': '',
        'Data type': 'A35',
        'Comment': '',
        'Example': 'Norfolk',
    },
    {
        'Field number': '23',
        'Field name': 'TO-ADDRESS-LINE-4',
        'Mandatory': '',
        'Data type': 'A35',
        'Comment': '',
        'Example': '',
    },
    {
        'Field number': '24',
        'Field name': 'TO-ADDRESS-LINE-5',
        'Mandatory': '',
        'Data type': 'A35',
        'Comment': '',
        'Example': '',
    },
    {
        'Field number': '25',
        'Field name': 'TO-POST-CODE',
        'Mandatory': 'Y',
        'Data type': 'A8',
        'Comment': """,
            Unformatted (ie. SA6 7JL not SA067JL) Must be present -
            PAF validation by Notify Must match PAF (in combination
            with TO-ADDRESS-LINE-1) to maximise postage discount
        """,
        'Example': 'NR1 5PQ',
    },
    {
        'Field number': '26',
        'Field name': 'RETURN-NAME',
        'Mandatory': '',
        'Data type': 'A40',
        'Comment': """
            This section added to handle return of undelivered mail
            to a specific organisational address may be required in
            a later release of the service.

            Not used by Notify at the moment.

            Given example:
                DWP Pension Service
        """,
        'Example': '',
    },
    {
        'Field number': '27',
        'Field name': 'RETURN-ADDRESS-LINE-1',
        'Mandatory': '',
        'Data type': 'A35',
        'Comment': """
            Not used by Notify at the moment.

            Given example:
                Mail Handling Site A
        """,
        'Example': '',
    },
    {
        'Field number': '28',
        'Field name': 'RETURN-ADDRESS-LINE-2',
        'Mandatory': '',
        'Data type': 'A35',
        'Comment': """
            Not used by Notify at the moment.

            Given example:
                Wolverhampton
        """,
        'Example': '',
    },
    {
        'Field number': '29',
        'Field name': 'RETURN-ADDRESS-LINE-3',
        'Mandatory': '',
        'Data type': 'A35',
        'Comment': '',
        'Example': '',
    },
    {
        'Field number': '30',
        'Field name': 'RETURN-ADDRESS-LINE-4',
        'Mandatory': '',
        'Data type': 'A35',
        'Comment': '',
        'Example': '',
    },
    {
        'Field number': '31',
        'Field name': 'RETURN-ADDRESS-LINE-5',
        'Mandatory': '',
        'Data type': 'A35',
        'Comment': '',
        'Example': '',
    },
    {
        'Field number': '32',
        'Field name': 'RETURN-POST-CODE',
        'Mandatory': '',
        'Data type': 'A8',
        'Comment': """
            Not used by Notify at the moment.

            Given example:
                WV9 1LU
        """,
        'Example': '',
    },
    {
        'Field number': '33',
        'Field name': 'SUBJECT-LINE',
        'Mandatory': '',
        'Data type': 'A120',
        'Comment': '',
        'Example': 'Your application is due soon',
    },
    {
        'Field number': '34',
        'Field name': 'NOTIFICATION-BODY',
        'Mandatory': '',
        'Data type': 'A',
        'Comment': """
            Difficult to define a maximum length as dependent on
            other formatting factors absolute maximum for OSG is 6
            pages but ideally no more than 4 pages total. OSG to
            confirm approach to mark up and line breaks...
        """,
        'Example': (
            'Dear Henry Hadlow,<cr><cr>'
            'Thank you for applying to register a lasting power of '
            'attorney (LPA) for property and financial affairs. We '
            'have checked your application and...<cr><cr>'
        ),
    }
]


@freeze_time("2016-04-29 12:00:00.000000")
@pytest.mark.parametrize('field', dvla_file_spec)
def test_letter_output_template(field):
    # To debug this test it’s helpful uncomment the following line:
    # print(field)
    template = LetterDVLATemplate(
        {
            "content": (
                'Dear ((name)),\n\n'
                'Thank you for applying to register a lasting power of '
                'attorney (LPA) for property and financial affairs. We '
                'have checked your application and...'
            ),
            'subject': 'Your ((thing)) is due soon',
        },
        {
            'thing': 'application',
            'name': 'Henry Hadlow',
            'address line 1': 'Mr Henry Hadlow',
            'address line 2': 'Managing Director',
            'address line 3': '123 Electric Avenue',
            'address line 4': 'Great Yarmouth',
            'address line 5': 'Norfolk',
            'address line 6': '',
            'postcode': 'NR1 5PQ',
        },
        numeric_id=1,
        contact_block='',
    )
    assert str(template).split('|')[int(field['Field number']) - 1] == field['Example']


def test_letter_output_pipe_delimiting():
    template = LetterDVLATemplate(
        {
            "content": 'Pipes | pipes | everywhere',
            'subject': 'Your | is due soon',
        },
        {
            'thing': '|',
            'name': '|',
            'address line 1': '|',
            'address line 2': 'Managing Director',
            'address line 3': '123 Electric Avenue',
            'address line 4': 'Great Yarmouth',
            'address line 5': 'Norfolk',
            'address line 6': '',
            'postcode': 'NR1 5PQ',
        },
        numeric_id=1,
    )

    assert len(str(template).split('|')) == len(dvla_file_spec)
    assert 'Pipes  pipes  everywhere' in str(template)


@pytest.mark.parametrize('id, expected_exception', [
    (None, 'numeric_id is required'),
    ('abc123', 'numeric_id must be an integer'),
    (12345678, 'numeric_id cannot be longer than 7 digits'),
    (1.34567, 'numeric_id must be an integer')
])
def test_letter_output_numeric_id(id, expected_exception):
    with pytest.raises(TypeError) as error:
        LetterDVLATemplate(
            {'content': '', 'subject': ''},
            numeric_id=id,
        )
    assert str(error.value) == expected_exception


def test_letter_output_stores_valid_numeric_id():
    assert LetterDVLATemplate(
        {'content': '', 'subject': ''},
        numeric_id=1234567,
    )._numeric_id == 1234567
