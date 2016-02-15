import pytest

from utils.placeholders import Placeholders


def test_class():
    assert str(Placeholders("hello ((name))")) == "hello ((name))"
    assert repr(Placeholders("hello ((name))")) == 'Placeholders("hello ((name))")'


@pytest.mark.parametrize(
    "template", [2, None, False]
)
def test_errors_for_invalid_template_types(template):

    with pytest.raises(TypeError):
        Placeholders(template)


@pytest.mark.parametrize(
    "template", [
        "",
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

    assert Placeholders(template).formatted == template
    assert Placeholders(template).replace({}) == template


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

    assert Placeholders(template).formatted == expected


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

    assert Placeholders(template).replace(data) == expected
