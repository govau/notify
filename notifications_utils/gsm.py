import unicodedata


GSM_CHARACTERS = set(
    '@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !"#¤%&\'()*+,-./0123456789:;<=>?' +
    '¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà' +
    # character set extension
    '^{}\\[~]|€'
)


REPLACEMENT_CHARACTERS = {
    '–': '-',  # EN DASH (U+2013)
    '—': '-',  # EM DASH (U+2014)
    '…': '...',  # HORIZONTAL ELLIPSIS (U+2026)
    '‘': '\'',  # LEFT SINGLE QUOTATION MARK (U+2018)
    '’': '\'',  # RIGHT SINGLE QUOTATION MARK (U+2019)
    '“': '"',  # LEFT DOUBLE QUOTATION MARK (U+201C)
    '”': '"',  # RIGHT DOUBLE QUOTATION MARK (U+201D)
    '\u200B': '',  # ZERO WIDTH SPACE (U+200B)
    '\t': ' ',  # TAB
}


def get_non_gsm_characters(content):
    return set(content) - GSM_CHARACTERS


def encode(content):
    """
    Given an input string, makes it GSM compatible. This involves removing all non-gsm characters by applying the
    following rules
    * characters within the GSM character set (https://en.wikipedia.org/wiki/GSM_03.38)
      and extension character set are kept

    * characters with sensible downgrades are replaced in place
        * characters with diacritics (accents, umlauts, cedillas etc) are replaced with their base character, eg é -> e
        * en dash and em dash (– and —) are replaced with hyphen (-)
        * left/right quotation marks (‘, ’, “, ”) are replaced with ' and "
        * zero width spaces (sometimes used to stop eg "gov.uk" linkifying) are removed
        * tabs are replaced with a single space

    * any remaining unicode characters (eg chinese/cyrillic/glyphs/emoji) are replaced with ?
    """
    return ''.join(encode_char(char) for char in content)


def get_unicode_char_from_codepoint(codepoint):
    """
    Given a unicode codepoint (eg 002E for '.', 0061 for 'a', etc), return that actual unicode character.

    unicodedata.decomposition returns strings containing codepoints, so we need to eval them ourselves
    """
    # lets just make sure we aren't evaling anything weird
    if not set(codepoint) <= set('0123456789ABCDEF') or not len(codepoint) == 4:
        raise ValueError('{} is not a valid unicode codepoint'.format(codepoint))
    return eval('"\\u{}"'.format(codepoint))


def encode_char(c):
    """
    Given a single unicode character, return a GSM compatible character.
    """
    # char is a GSM character already - return that native character.
    if c in GSM_CHARACTERS:
        return c
    else:
        decomposed = unicodedata.decomposition(c)
        if decomposed != '' and '<compat>' not in decomposed:
            # if there is a decomposition, which is not a compatibility decomposition (eg … -> ...),
            # then it's probably a letter with a modifier, eg á
            # ASSUMPTION: The first character of a combined unicode character (eg 'á' == '0061 0301')
            # will be the ascii char
            return get_unicode_char_from_codepoint(decomposed.split()[0])
        else:
            # try and find a mapping (eg en dash -> hyphen ('–': '-')), else return a '?'
            return REPLACEMENT_CHARACTERS.get(c, '?')
