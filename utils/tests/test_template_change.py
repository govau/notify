import pytest
from notifications_utils.template import Template
from notifications_utils.template_change import TemplateChange


@pytest.mark.parametrize(
    "old_template, new_template, should_differ", [
        (
            Template({'content': '((1)) ((2)) ((3))'}),
            Template({'content': '((1)) ((2)) ((3))'}),
            False
        ),
        (
            Template({'content': '((1)) ((2)) ((3))'}),
            Template({'content': '((3)) ((2)) ((1))'}),
            False
        ),
        (
            Template({'content': '((1)) ((2)) ((3))'}),
            Template({'content': '((1)) ((1)) ((2)) ((2)) ((3)) ((3))'}),
            False
        ),
        (
            Template({'content': '((1))'}),
            Template({'content': '((1)) ((2))'}),
            True
        ),
        (
            Template({'content': '((1)) ((2))'}),
            Template({'content': '((1))'}),
            True
        ),
        (
            Template({'content': '((a)) ((b))'}),
            Template({'content': '((A)) (( B_ ))'}),
            False
        ),
    ]
)
def test_checking_for_difference_between_templates(old_template, new_template, should_differ):
    assert TemplateChange(old_template, new_template).has_different_placeholders == should_differ


@pytest.mark.parametrize(
    "old_template, new_template, placeholders_added", [
        (
            Template({'content': '((1)) ((2)) ((3))'}),
            Template({'content': '((1)) ((2)) ((3))'}),
            set()
        ),
        (
            Template({'content': '((1)) ((2)) ((3))'}),
            Template({'content': '((1)) ((1)) ((2)) ((2)) ((3)) ((3))'}),
            set()
        ),
        (
            Template({'content': '((1)) ((2)) ((3))'}),
            Template({'content': '((1))'}),
            set()
        ),
        (
            Template({'content': '((1))'}),
            Template({'content': '((1)) ((2)) ((3))'}),
            set(['2', '3'])
        ),
        (
            Template({'content': '((a))'}),
            Template({'content': '((A)) ((B)) ((C))'}),
            set(['B', 'C'])
        ),
    ]
)
def test_placeholders_added(old_template, new_template, placeholders_added):
    assert TemplateChange(old_template, new_template).placeholders_added == placeholders_added


@pytest.mark.parametrize(
    "old_template, new_template, placeholders_removed", [
        (
            Template({'content': '((1)) ((2)) ((3))'}),
            Template({'content': '((1)) ((2)) ((3))'}),
            set()
        ),
        (
            Template({'content': '((1)) ((2)) ((3))'}),
            Template({'content': '((1)) ((1)) ((2)) ((2)) ((3)) ((3))'}),
            set()
        ),
        (
            Template({'content': '((1))'}),
            Template({'content': '((1)) ((2)) ((3))'}),
            set()
        ),
        (
            Template({'content': '((1)) ((2)) ((3))'}),
            Template({'content': '((1))'}),
            set(['2', '3'])
        ),
        (
            Template({'content': '((a)) ((b)) ((c))'}),
            Template({'content': '((A))'}),
            set(['b', 'c'])
        ),
    ]
)
def test_placeholders_removed(old_template, new_template, placeholders_removed):
    assert TemplateChange(old_template, new_template).placeholders_removed == placeholders_removed
