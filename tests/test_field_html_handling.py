import pytest
from notifications_utils.field import Field


@pytest.mark.parametrize('content, values, expected_stripped, expected_escaped', [
    (
        'string <em>with</em> html',
        {},
        'string with html',
        'string &lt;em&gt;with&lt;/em&gt; html',
    ),
    (
        'string ((<em>with</em>)) html',
        {},
        'string <span class=\'placeholder\'>((with))</span> html',
        'string <span class=\'placeholder\'>((&lt;em&gt;with&lt;/em&gt;))</span> html',
    ),
    (
        'string ((placeholder)) html',
        {'placeholder': '<em>without</em>'},
        'string without html',
        'string &lt;em&gt;without&lt;/em&gt; html',
    ),
    (
        'string ((<em>optional</em>??<em>placeholder</em>)) html',
        {},
        'string <span class=\'placeholder-conditional\'>((optional??</span>placeholder)) html',
        (
            'string '
            '<span class=\'placeholder-conditional\'>'
            '((&lt;em&gt;optional&lt;/em&gt;??</span>'
            '&lt;em&gt;placeholder&lt;/em&gt;)) '
            'html'
        ),
    ),
    (
        'string ((optional??<em>placeholder</em>)) html',
        {'optional': True},
        'string placeholder html',
        'string &lt;em&gt;placeholder&lt;/em&gt; html',
    ),
    (
        'string & entity',
        {},
        'string &amp; entity',
        'string &amp; entity',
    ),
])
def test_field_handles_html(content, values, expected_stripped, expected_escaped):
    assert str(Field(content, values)) == expected_stripped
    assert str(Field(content, values, html='strip')) == expected_stripped
    assert str(Field(content, values, html='escape')) == expected_escaped
