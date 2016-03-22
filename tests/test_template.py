import pytest

from flask import Markup
from utils.template import Template, NeededByTemplateError, NoPlaceholderForDataError


def test_class():
    template = {"content": "hello ((name))"}
    assert str(Template(template)) == "hello ((name))"
    assert str(Template(template, {'name': 'Chris'})) == 'hello Chris'
    assert repr(Template(template)) == 'Template("hello ((name))", {})'


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
            "the<br>                quick brown<br><br>                fox",
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
    assert Template({"content": template_content}).formatted == expected_formatted
    assert Template({"content": template_content}).replaced == expected_replaced


@pytest.mark.parametrize(
    "template_content,prefix,expected", [
        ("the quick brown fox", None, "the quick brown fox"),
        ("the quick brown fox", "Vehicle tax", "Vehicle tax: the quick brown fox"),
        ("the quick brown fox", "((service name))", "((service name)): the quick brown fox")
    ]
)
def test_prefixing_template_with_service_name(template_content, prefix, expected):
    assert Template({"content": template_content, 'template_type': 'sms'}, prefix=prefix).formatted == expected
    assert Template({"content": template_content, 'template_type': 'sms'}, prefix=prefix).replaced == expected
    assert Template({"content": template_content, 'template_type': 'sms'}, prefix=prefix).content == template_content
    assert Template({"content": template_content}, prefix=prefix).replaced == template_content
    assert Template({"content": template_content}, prefix=prefix).formatted == template_content


@pytest.mark.parametrize(
    "template_content,expected", [
        (
            "((colour))",
            "<span class='placeholder'>colour</span>"
        ),
        (
            "the quick ((colour)) fox",
            "the quick <span class='placeholder'>colour</span> fox"
        ),
        (
            "((article)) quick ((colour)) ((animal))",
            "<span class='placeholder'>article</span> quick <span class='placeholder'>colour</span> <span class='placeholder'>animal</span>"  # noqa
        ),
        (
            """
                ((article)) quick
                ((colour))
                ((animal))
            """,
            "<span class='placeholder'>article</span> quick<br>                <span class='placeholder'>colour</span><br>                <span class='placeholder'>animal</span>"  # noqa
        ),
        (
            "the quick (((colour))) fox",
            "the quick (<span class='placeholder'>colour</span>) fox"
        ),
    ]
)
def test_formatting_of_placeholders(template_content, expected):
    assert Template({"content": template_content}).formatted == expected


def test_formatting_of_template_contents_as_markup():
    assert Template(
        {"content": "Hello ((name))"}
    ).formatted_as_markup == Markup("Hello <span class='placeholder'>name</span>")


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
    ]
)
def test_replacement_of_placeholders(template_content, data, expected):
    assert Template({"content": template_content}, data).replaced == expected


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
        drop_values=('animal', 'adjective')
    ).replaced == 'the quick brown fox jumps over the brown dog'
    # make sure that our template and values aren’t modified
    assert Template(template, values).missing_data == []


def test_html_email_template():
    template = Template(
        {"content": '''
            the quick ((colour)) ((animal))

            jumped over the lazy dog
        '''},
        {'animal': 'fox', 'colour': 'brown'}
    )
    assert '<html>' in template.as_HTML_email
    print(template.as_HTML_email)
    assert "the quick brown fox<br><br>            jumped over the lazy dog" in template.as_HTML_email


@pytest.mark.parametrize(
    "template_content,expected", [
        (
            "the quick brown fox",
            []
        ),
        (
            "the quick ((colour)) fox",
            ["colour"]
        ),
        (
            "the quick ((colour)) ((animal))",
            ["colour", "animal"]
        ),
        (
            "((colour)) ((animal)) ((colour)) ((animal))",
            ["colour", "animal"]
        ),
    ]
)
def test_extracting_placeholders(template_content, expected):
    assert Template({"content": template_content}).placeholders == expected


def test_extracting_placeholders_marked_up():
    assert Template({"content": "the quick ((colour)) ((animal))"}).placeholders_as_markup == [
        Markup(u"<span class='placeholder'>colour</span>"),
        Markup(u"<span class='placeholder'>animal</span>")
    ]
