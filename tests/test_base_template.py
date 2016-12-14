import pytest
from unittest.mock import PropertyMock
from unittest.mock import patch
from flask import Markup
from notifications_utils.template import (
    Template,
    HTMLEmailTemplate,
    SMSMessageTemplate,
    LetterPreviewTemplate,
    NeededByTemplateError,
    NoPlaceholderForDataError,
    WithSubjectTemplate
)


def test_class():
    assert repr(
        Template({"content": "hello ((name))"})
    ) == 'Template("hello ((name))", {})'


def test_passes_through_template_attributes():
    assert Template({"content": ''}).name is None
    assert Template({"content": '', 'name': 'Two week reminder'}).name == 'Two week reminder'
    assert Template({"content": ''}).id is None
    assert Template({"content": '', 'id': '1234'}).id == '1234'
    assert Template({"content": ''}).template_type is None
    assert Template({"content": '', 'template_type': 'sms'}).template_type is 'sms'
    assert not hasattr(Template({"content": ''}), 'subject')


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
    assert WithSubjectTemplate({"content": template_content, 'subject': template_subject}).placeholders == expected


@pytest.mark.parametrize(
    "content,prefix, expected_length, expected_replaced_length",
    [
        ("The quick brown fox jumped over the lazy dog", None, 44, 44),
        ("深", None, 3, 3),
        ("'First line.\n", None, 12, 12),
        ("\t\n\r", None, 0, 0),
        ("((placeholder))", None, 15, 3),
        ("((placeholder))", 'Service name', 29, 17),
        ("Foo", '((placeholder))', 20, 20),  # placeholder doesn’t work in service name
    ])
def test_get_character_count_of_content(content, prefix, expected_length, expected_replaced_length):
    template = SMSMessageTemplate(
        {'content': content},
    )
    template.prefix = prefix
    template.sender = None
    assert template.content_count == expected_length
    template.values = {'placeholder': '123'}
    assert template.content_count == expected_replaced_length


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
        'notifications_utils.template.SMSMessageTemplate.content_count',
        new_callable=PropertyMock
    ) as mocked:
        mocked.return_value = char_count
        template = SMSMessageTemplate({'content': 'faked', 'template_type': 'sms'})
        assert template.fragment_count == expected_sms_fragment_count


def test_random_variable_retrieve():
    template = Template({'content': 'content', 'template_type': 'sms', 'created_by': "now"})
    assert template.get_raw('created_by') == "now"
    assert template.get_raw('missing', default='random') == 'random'
    assert template.get_raw('missing') is None


def test_compare_template():
    with patch(
        'notifications_utils.template_change.TemplateChange.__init__',
        return_value=None
    ) as mocked:
        old_template = Template({'content': 'faked', 'template_type': 'sms'})
        new_template = Template({'content': 'faked', 'template_type': 'sms'})
        template_changes = old_template.compare_to(new_template)
        mocked.assert_called_once_with(old_template, new_template)
