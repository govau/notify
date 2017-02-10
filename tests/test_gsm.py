import pytest

from notifications_utils import gsm


params, ids = zip(
    (('a', 'a'), 'ascii char (a)'),
    # ascii control chars (in GSM)
    (('\n', '\n'), 'ascii control char in gsm (newline)'),
    (('\r', '\r'), 'ascii control char in gsm (return)'),
    # ascii control char (not in GSM)
    (('\t', ' '), 'ascii control char not in gsm (tab)'),
    # this is in GSM charset so is preserved
    (('à', 'à'), 'non-ascii gsm char (a with accent)'),
    (('€', '€'), 'non-ascii gsm char (euro)'),
    # thes are not in GSM charset so are downgraded
    (('â', 'a'), 'decomposed unicode char (a with hat)'),
    (('ç', 'c'), 'decomposed unicode char (C with cedilla)'),
    # these unicode chars should change to something completely different for compatibility
    (('–', '-'), 'compatibility transform unicode char (EN DASH (U+2013)'),
    (('—', '-'), 'compatibility transform unicode char (EM DASH (U+2014)'),
    (('…', '...'), 'compatibility transform unicode char (HORIZONTAL ELLIPSIS (U+2026)'),
    (('\u200B', ''), 'compatibility transform unicode char (ZERO WIDTH SPACE (U+200B)'),
    (('‘', '\''), 'compatibility transform unicode char (LEFT SINGLE QUOTATION MARK (U+2018)'),
    (('’', '\''), 'compatibility transform unicode char (RIGHT SINGLE QUOTATION MARK (U+2019)'),
    (('“', '"'), 'compatibility transform unicode char (LEFT DOUBLE QUOTATION MARK (U+201C)	'),
    (('”', '"'), 'compatibility transform unicode char (RIGHT DOUBLE QUOTATION MARK (U+201D)'),
    # this unicode char is not decomposable
    (('😬', '?'), 'undecomposable unicode char (grimace emoji)'),
)


@pytest.mark.parametrize('char, expected', params, ids=ids)
def test_encode_char(char, expected):
    assert gsm.encode_char(char) == expected


@pytest.mark.parametrize('codepoint, char', [
    ('0041', 'A'),
    ('0061', 'a'),
])
def test_get_unicode_char_from_codepoint(codepoint, char):
    assert gsm.get_unicode_char_from_codepoint(codepoint) == char


@pytest.mark.parametrize('bad_input', [
    '',
    'GJ',
    '00001',
    '0001";import sys;sys.exit(0)"'
])
def test_get_unicode_char_from_codepoint_rejects_bad_input(bad_input):
    with pytest.raises(ValueError):
        gsm.get_unicode_char_from_codepoint(bad_input)


@pytest.mark.parametrize('content, expected', [
    ('Łódź', '?odz'),
    ('The quick brown fox jumps over the lazy dog', 'The quick brown fox jumps over the lazy dog'),
])
def test_encode_string(content, expected):
    assert gsm.encode(content) == expected


@pytest.mark.parametrize('content, expected', [
    ('The quick brown fox jumps over the lazy dog', set()),
    ('The “quick” brown fox has some downgradable characters', {'“', '”'}),
    ('Need more 🐮🔔', {'🐮', '🔔'})
])
def test_get_non_gsm_characters(content, expected):
    assert gsm.get_non_gsm_characters(content) == expected
