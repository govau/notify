import pytest
from functools import partial
from unittest.mock import PropertyMock
from unittest.mock import patch
from flask import Markup
from notifications_utils.template import Template, NeededByTemplateError, NoPlaceholderForDataError
from notifications_utils.renderers import HTMLEmail, EmailPreview, SMSPreview, LetterPreview, PassThrough


def test_class():
    template = {"content": "hello ((name))"}
    assert str(Template(template, renderer=PassThrough())) == "hello ((name))"
    assert str(Template(template, {'name': 'Chris'}, renderer=PassThrough())) == 'hello Chris'
    assert repr(Template(template, renderer=PassThrough())) == 'Template("hello ((name))", {})'


def test_passes_through_template_attributes():
    assert Template({"content": ''}).name is None
    assert Template({"content": '', 'name': 'Two week reminder'}).name == 'Two week reminder'
    assert Template({"content": ''}).id is None
    assert Template({"content": '', 'id': '1234'}).id == '1234'
    assert Template({"content": ''}).template_type is None
    assert Template({"content": '', 'template_type': 'sms'}).template_type is 'sms'
    assert Template({"content": ''}).subject is None
    assert Template({"content": '', 'subject': 'Your tax is due'}).subject == 'Your tax is due'


def test_errors_for_missing_template_content():
    with pytest.raises(KeyError):
        Template({})


@pytest.mark.parametrize(
    "template", [0, 1, 2, True, False, None]
)
def test_errors_for_invalid_template_types(template):
    with pytest.raises(TypeError):
        Template(template)


@pytest.mark.parametrize(
    "values", [[], False]
)
def test_errors_for_invalid_values(values):
    with pytest.raises(TypeError):
        Template({"content": ''}, values)


def test_sets_default_renderer():
    assert isinstance(
        Template({'content': ''}).renderer,
        EmailPreview
    )


@pytest.mark.parametrize("template_type, expected_renderer", [
    ('sms', SMSPreview),
    ('email', EmailPreview),
    ('letter', LetterPreview)
])
def test_sets_correct_renderer(template_type, expected_renderer):
    assert isinstance(
        Template({'content': '', 'template_type': template_type}).renderer,
        expected_renderer
    )


def test_passes_subject_through_to_letter_renderer():
    assert Template(
        {'content': '', 'template_type': 'letter', 'subject': 'Your thing is due'}
    ).renderer.subject == 'Your thing is due'


def test_matches_keys_to_placeholder_names():

    template = Template({"content": "hello ((name))"})

    template.values = {'NAME': 'Chris'}
    assert template.values == {'name': 'Chris'}

    template.values = {'NAME': 'Chris', 'Town': 'London'}
    assert template.values == {'name': 'Chris', 'Town': 'London'}
    assert template.additional_data == {'Town'}

    template.values = None
    assert template.missing_data == ['name']


@pytest.mark.parametrize(
    "template_content,expected_formatted,expected_replaced", [
        ("", "", ""),
        ("the quick brown fox", "the quick brown fox", "the quick brown fox"),
        (
            """
                the
                quick brown

                fox
            """,
            """
                the
                quick brown

                fox
            """,
            """
                the
                quick brown

                fox
            """
        ),
        ("the ((quick brown fox", "the ((quick brown fox", "the ((quick brown fox"),
        ("the (()) brown fox", "the (()) brown fox", "the (()) brown fox")
    ]
)
def test_returns_a_string_without_placeholders(template_content, expected_formatted, expected_replaced):
    assert Template({"content": template_content}, renderer=PassThrough())._raw_formatted == expected_formatted
    assert Template({"content": template_content}, renderer=PassThrough()).replaced == expected_replaced


@pytest.mark.parametrize(
    "template_content,prefix,expected", [
        ("the quick brown fox", None, "the quick brown fox"),
        ("the quick brown fox", "Vehicle tax", "Vehicle tax: the quick brown fox"),
        ("the quick brown fox", "((service name))", "((service name)): the quick brown fox")
    ]
)
def test_prefixing_template_with_service_name(template_content, prefix, expected):
    assert Template({"content": template_content, 'template_type': 'sms'}, prefix=prefix)._raw_formatted == expected
    assert Template({"content": template_content, 'template_type': 'sms'}, prefix=prefix).replaced == expected
    assert Template(
        {"content": template_content, 'template_type': 'sms'}, prefix=prefix, sms_sender='Something'
    ).replaced == "the quick brown fox"
    assert Template({"content": template_content, 'template_type': 'sms'}, prefix=prefix).content == template_content
    assert Template({"content": template_content}, prefix=prefix, renderer=PassThrough()).replaced == template_content
    assert Template(
        {"content": template_content}, prefix=prefix, renderer=PassThrough()
    )._raw_formatted == template_content


@pytest.mark.parametrize(
    "template_content,expected", [
        (
            "((colour))",
            "<span class='placeholder'>((colour))</span>"
        ),
        (
            "the quick ((colour)) fox",
            "the quick <span class='placeholder'>((colour))</span> fox"
        ),
        (
            "((article)) quick ((colour)) ((animal))",
            "<span class='placeholder'>((article))</span> quick <span class='placeholder'>((colour))</span> <span class='placeholder'>((animal))</span>"  # noqa
        ),
        (
            """
                ((article)) quick
                ((colour))
                ((animal))
            """,
            """
                <span class='placeholder'>((article))</span> quick
                <span class='placeholder'>((colour))</span>
                <span class='placeholder'>((animal))</span>
            """
        ),
        (
            "the quick (((colour))) fox",
            "the quick (<span class='placeholder'>((colour))</span>) fox"
        ),
        (
            "((warning?))",
            "<span class='placeholder'>((warning?))</span>"
        ),
        (
            "((warning? This is not a conditional))",
            "<span class='placeholder'>((warning? This is not a conditional))</span>"
        ),
        (
            "((warning?? This is a warning))",
            "<span class='placeholder-conditional'>((warning??</span> This is a warning))"
        ),
    ]
)
def test_formatting_of_placeholders(template_content, expected):
    assert Template({"content": template_content}, renderer=PassThrough())._raw_formatted == expected


@pytest.mark.parametrize(
    "template_subject, expected", [
        (
            "(( name ))",
            "<span class='placeholder'>(( name ))</span>"
        ), (
            "the quick (( animal ))",
            "the quick <span class='placeholder'>(( animal ))</span>"
        ), (
            "(( person )) eats (( food ))",
            "<span class='placeholder'>(( person ))</span> eats <span class='placeholder'>(( food ))</span>"
        ), (
            "the quick (((colour))) fox",
            "the quick (<span class='placeholder'>((colour))</span>) fox"
        )
    ]
)
def test_subject_formatting_of_placeholders(template_subject, expected):
    assert Template({'subject': template_subject, 'content': ''})._raw_formatted_subject == expected


def test_formatting_of_template_contents_as_markup():
    assert Template(
        {"content": "Hello ((name))"}, renderer=PassThrough()
    ).formatted_as_markup == Markup("Hello <span class='placeholder'>name</span>")


def test_formatting_of_template_contents_as_markup():
    assert Template(
        {"content": "", "subject": "Hello ((name))"}, renderer=PassThrough()
    ).formatted_subject == Markup("Hello <span class='placeholder'>((name))</span>")


@pytest.mark.parametrize(
    "template_content,data,expected", [
        (
            "((colour))",
            {"colour": "red"},
            "red"
        ),
        (
            "the quick ((colour)) fox",
            {"colour": "brown"},
            "the quick brown fox"
        ),
        (
            "((article)) quick ((colour)) ((animal))",
            {"article": "the", "colour": "brown", "animal": "fox"},
            "the quick brown fox"
        ),
        (
            "the quick (((colour))) fox",
            {"colour": "brown"},
            "the quick (brown) fox"
        ),
        (
            "the quick ((colour)) fox",
            {"colour": "<script>alert('foo')</script>"},
            "the quick alert('foo') fox"
        ),
        (
            "((warning?))",
            {"warning?": "This is not a conditional"},
            "This is not a conditional"
        ),
        (
            "((warning?warning))",
            {"warning?warning": "This is not a conditional"},
            "This is not a conditional"
        ),
        (
            "((warning??This is a conditional warning))",
            {"warning": True},
            "This is a conditional warning"
        ),
        (
            "((warning??This is a conditional warning))",
            {"warning": False},
            ""
        ),
    ]
)
def test_replacement_of_placeholders(template_content, data, expected):
    assert Template(
        {"content": template_content}, data, renderer=PassThrough()
    ).replaced == expected


@pytest.mark.parametrize(
    "template_content,template_subject,data,expected_content,expected_subject", [
        (
            "No placeholder content",
            "((name))",
            {'name': 'Vladimir'},
            "No placeholder content",
            "Vladimir"
        ), (
            "My name is ((name))",
            "((name))",
            {"name": "Vladimir"},
            "My name is Vladimir",
            "Vladimir"
        ), (
            "The quick brown fox jumped over the lazy dog",
            "The quick ((colour)) fox jumped over the lazy ((dog))",
            {"colour": "brown", "dog": "cat"},
            "The quick brown fox jumped over the lazy dog",
            "The quick brown fox jumped over the lazy cat"
        ), (
            "(((random)))",
            "(( :) ))",
            {"random": ":(", ":)": "smiley"},
            "(:()",
            "(( :) ))"
        )
    ])
def test_replacement_of_placeholders_subject(template_content,
                                             template_subject,
                                             data,
                                             expected_content,
                                             expected_subject):
    template = Template({"content": template_content, 'subject': template_subject}, data, renderer=PassThrough())
    assert template.replaced == expected_content
    assert template.replaced_subject == expected_subject


def test_replacement_of_template_with_incomplete_data():
    with pytest.raises(NeededByTemplateError) as error:
        Template(
            {"content": "the quick ((colour)) ((animal)) ((verb)) over the ((colour)) dog"},
            {'animal': 'fox', 'adjective': 'lazy'}
        ).replaced
    assert "colour, verb" == str(error.value)


def test_can_drop_additional_values():
    values = {'colour': 'brown', 'animal': 'fox', 'adjective': 'lazy'}
    template = {"content": "the quick ((colour)) fox jumps over the ((colour)) dog"}
    assert Template(
        template,
        values,
        drop_values=('animal', 'adjective'),
        renderer=PassThrough()
    ).replaced == 'the quick brown fox jumps over the brown dog'
    # make sure that our template and values aren’t modified
    assert Template(template, values).missing_data == []


def test_html_email_template():
    template = Template(
        {"content": (
            'the quick ((colour)) ((animal))\n'
            '\n'
            'jumped over the lazy dog'
        )},
        {'animal': 'fox', 'colour': 'brown'},
        renderer=HTMLEmail()
    )
    assert '<html>' in template.replaced
    assert (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        'the quick brown fox</p>'
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        'jumped over the lazy dog</p>'
    ) in template.replaced


@pytest.mark.parametrize(
    "template_content, template_subject, expected", [
        (
            "the quick brown fox",
            "jumps",
            []
        ),
        (
            "the quick ((colour)) fox",
            "jumps",
            ["colour"]
        ),
        (
            "the quick ((colour)) ((animal))",
            "jumps",
            ["colour", "animal"]
        ),
        (
            "((colour)) ((animal)) ((colour)) ((animal))",
            "jumps",
            ["colour", "animal"]
        ),
        (
            "the quick brown fox",
            "((colour))",
            ["colour"]
        ),
        (
            "the quick ((colour)) ",
            "((animal))",
            ["animal", "colour"]
        ),
        (
            "((colour)) ((animal)) ",
            "((colour)) ((animal))",
            ["colour", "animal"]
        ),
        (
            "Dear ((name)), ((warning?? This is a warning))",
            "",
            ["name", "warning"]
        ),
        (
            "((warning? one question mark))",
            "",
            ["warning? one question mark"]
        )
    ]
)
def test_extracting_placeholders(template_content, template_subject, expected):
    assert Template({"content": template_content, 'subject': template_subject}).placeholders == expected


@pytest.mark.parametrize(
    "content,prefix,encoding,expected_length",
    [
        ("The quick brown fox jumped over the lazy dog", None, "utf-8", 44),
        ("深", None, "utf-8", 3),
        ("'First line.\n", None, 'utf-8', 12),
        ("\t\n\r", None, 'utf-8', 0),
        ("((placeholder))", 'Service name', "utf-8", 17),
    ])
def test_get_character_count_of_content(content, prefix, encoding, expected_length):
    template = Template(
        {'content': content, 'template_type': 'sms'},
        encoding=encoding,
        prefix=prefix,
        values={'placeholder': '123'}
    )
    assert template.replaced_content_count == expected_length


@pytest.mark.parametrize(
    "char_count, expected_sms_fragment_count",
    [
        (159, 1),
        (160, 1),
        (161, 2),
        (306, 2),
        (307, 3),
        (459, 3),
        (460, 4),
        (461, 4)
    ])
def test_sms_fragment_count(char_count, expected_sms_fragment_count):
    with patch(
        'notifications_utils.template.Template.replaced_content_count',
        new_callable=PropertyMock
    ) as mocked:
        mocked.return_value = char_count
        template = Template({'content': 'faked', 'template_type': 'sms'})
        assert template.sms_fragment_count == expected_sms_fragment_count


@pytest.mark.parametrize(
    "content_count, limit, too_long",
    [
        (3, 2, True),
        (2, 3, False),
        (1, None, False)
    ])
def test_content_limit(content_count, limit, too_long):
    with patch(
        'notifications_utils.template.Template.replaced_content_count',
        new_callable=PropertyMock
    ) as mocked:
        mocked.return_value = content_count
        template = Template(
            {'content': 'faked', 'template_type': 'sms'},
            content_character_limit=limit
        )
        assert template.content_too_long == too_long


def test_random_variable_retrieve():
    template = Template({'content': 'content', 'template_type': 'sms', 'created_by': "now"})
    assert template.get_raw('created_by') == "now"
    assert template.get_raw('missing', default='random') == 'random'
    assert template.get_raw('missing') is None


def test_compare_template():
    with patch(
        'notifications_utils.template.TemplateChange.__init__',
        return_value=None
    ) as mocked:
        old_template = Template({'content': 'faked', 'template_type': 'sms'})
        new_template = Template({'content': 'faked', 'template_type': 'sms'})
        template_changes = old_template.compare_to(new_template)
        mocked.assert_called_once_with(old_template, new_template)
