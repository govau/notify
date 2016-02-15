import pytest

from utils.placeholders import Placeholders


def test_errors_forempty_templates():
    assert str(Placeholders("hello ((name))")) == "hello ((name))"
    assert repr(Placeholders("hello ((name))")) == 'Placeholders("hello ((name))")'

    with pytest.raises(TypeError):
        Placeholders().format_placeholders()

    with pytest.raises(TypeError):
        assert Placeholders().format_placeholders(2)

    assert Placeholders().format_placeholders("") == ""
    assert Placeholders().format_placeholders(None) == None
    assert Placeholders().format_placeholders(False) == False


@pytest.mark.parametrize(
    "template", [
        "the quick brown fox",
        """
            the
            quick brown

            fox
        """,
        "the ((quick brown fox",
        "the (()) brown fox"
    ]
)
def test_returns_a_string_without_placeholders(template):

    assert Placeholders().format_placeholders(template) == template
    assert Placeholders().replace_placeholders(template, {}) == template


@pytest.mark.parametrize(
    "template,expected", [
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
            """
                <span class='placeholder'>article</span> quick
                <span class='placeholder'>colour</span>
                <span class='placeholder'>animal</span>
            """
        ),
        (
            "the quick (((colour))) fox",
            "the quick (<span class='placeholder'>colour</span>) fox"
        ),
    ]
)
def test_formatting_of_placeholders(template, expected):

    assert Placeholders().format_placeholders(template) == expected


@pytest.mark.parametrize(
    "template,data,expected", [
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
def test_replacement_of_placeholders(template, data, expected):

    assert Placeholders().replace_placeholders(template, data) == expected
