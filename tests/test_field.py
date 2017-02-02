import pytest
from notifications_utils.field import Field, str2bool


@pytest.mark.parametrize("content", [
    "",
    "the quick brown fox",
    """
        the
        quick brown

        fox
    """,
    "the ((quick brown fox",
    "the (()) brown fox",
])
def test_returns_a_string_without_placeholders(content):
    assert str(Field(content)) == content


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
    assert str(Field(template_content, data)) == expected


@pytest.mark.parametrize(
    "content,expected", [
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
def test_formatting_of_placeholders(content, expected):
    assert str(Field(content)) == expected


@pytest.mark.parametrize(
    "content, values, expected", [
        (
            "((name)) ((colour))",
            {'name': 'Jo'},
            "Jo <span class='placeholder'>((colour))</span>",
        ),
        (
            "((show_thing??thing)) ((colour))",
            {'colour': 'red'},
            "<span class='placeholder-conditional'>((show_thing??</span>thing)) red",
        ),
    ]
)
def test_handling_of_missing_values(content, values, expected):
    assert str(Field(content, values)) == expected


@pytest.mark.parametrize(
    "value", [
        '0',
        0, 2, 99.99999,
        'off',
        'exclude',
        'no'
        'any random string',
        'false',
        False,
        [], {}, (),
        ['true'], {'True': True}, (True, 'true', 1)
    ]
)
def test_what_will_not_trigger_optional_placeholder(value):
    assert str2bool(value) is False


@pytest.mark.parametrize(
    "value", [
        1,
        '1',
        'yes',
        'y',
        'true',
        'True',
        True,
        'include',
        'show'
    ]
)
def test_what_will_trigger_optional_placeholder(value):
    assert str2bool(value) is True
