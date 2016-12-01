import pytest
from unittest.mock import PropertyMock
from unittest.mock import patch
from notifications_utils.template import Template
from notifications_utils.renderers import HTMLEmail, EmailPreview, SMSPreview, SMSMessage, LetterPreview, PassThrough


def test_class():
    assert repr(
        Template({"content": "hello ((name))"}, renderer=PassThrough())
    ) == 'Template("hello ((name))", {})'


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


def test_matches_keys_to_placeholder_names():

    template = Template({"content": "hello ((name))"})

    template.values = {'NAME': 'Chris'}
    assert template.values == {'name': 'Chris'}

    template.values = {'NAME': 'Chris', 'Town': 'London'}
    assert template.values == {'name': 'Chris', 'Town': 'London'}
    assert template.additional_data == {'Town'}

    template.values = None
    assert template.missing_data == ['name']


def test_can_drop_additional_values():
    values = {'colour': 'brown', 'animal': 'fox', 'adjective': 'lazy'}
    template = {"content": "the quick ((colour)) fox jumps over the ((colour)) dog"}
    assert Template(
        template,
        values,
        drop_values=('animal', 'adjective'),
        renderer=PassThrough()
    ).rendered == 'the quick brown fox jumps over the brown dog'
    # make sure that our template and values aren’t modified
    assert Template(template, values).missing_data == []


@pytest.mark.parametrize(
    'renderer', [HTMLEmail, LetterPreview]
)
def test_markdown_in_templates(renderer):
    template = Template(
        {
            "content": (
                'the quick ((colour)) ((animal))\n'
                '\n'
                'jumped over the lazy dog'
            ),
            'subject': 'animal story'
        },
        {'animal': 'fox', 'colour': 'brown'},
        renderer=renderer()
    )
    assert (
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        'the quick brown fox</p>'
        '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">'
        'jumped over the lazy dog</p>'
    ) in template.rendered


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
    "content,prefix,expected_length",
    [
        ("The quick brown fox jumped over the lazy dog", None, 44),
        ("深", None, 3),
        ("'First line.\n", None, 12),
        ("\t\n\r", None, 0),
        ("((placeholder))", 'Service name', 17),
    ])
def test_get_character_count_of_content(content, prefix, expected_length):
    template = Template(
        {'content': content},
        values={'placeholder': '123'},
        renderer=SMSMessage(prefix=prefix)
    )
    assert template.content_count == expected_length


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
        'notifications_utils.template.Template.content_count',
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
        'notifications_utils.template.Template.content_count',
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
