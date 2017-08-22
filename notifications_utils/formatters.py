import re
import urllib

import mistune
import bleach
from flask import Markup
from notifications_utils import gsm
import smartypants

mistune._block_quote_leading_pattern = re.compile(r'^ *\^ ?', flags=re.M)
mistune.BlockGrammar.block_quote = re.compile(r'^( *\^[^\n]+(\n[^\n]+)*\n*)+')
mistune.BlockGrammar.list_block = re.compile(
    r'^( *)([*+-]|\d+\.)[\s\S]+?'
    r'(?:'
    r'\n+(?=\1?(?:[-*_] *){3,}(?:\n+|$))'  # hrule
    r'|\n+(?=%s)'  # def links
    r'|\n+(?=%s)'  # def footnotes
    r'|\n{2,}'
    r'(?! )'
    r'(?!\1(?:[*+-]|\d+\.) )\n*'
    r'|'
    r'\s*$)' % (
        mistune._pure_pattern(mistune.BlockGrammar.def_links),
        mistune._pure_pattern(mistune.BlockGrammar.def_footnotes),
    )
)
mistune.BlockGrammar.list_item = re.compile(
    r'^(( *)(?:[*+-]|\d+\.)[^\n]*'
    r'(?:\n(?!\2(?:[*+-]|\d+\.))[^\n]*)*)',
    flags=re.M
)
mistune.BlockGrammar.list_bullet = re.compile(r'^ *(?:[*+-]|\d+\.)')

govuk_not_a_link = re.compile(
    r'(?<!\.|\/)(GOV)\.(UK)(?!\/|\?)',
    re.IGNORECASE
)

dvla_markup_tags = re.compile(
    str('|'.join('\<{}\>'.format(tag) for tag in {
        'cr', 'h1', 'h2', 'p', 'normal', 'op', 'np', 'bul', 'tab'
    })),
    re.IGNORECASE
)

smartypants.tags_to_skip = smartypants.tags_to_skip + ['a']

whitespace_before_punctuation = re.compile(r'\s+([,|\.])')

hyphens_surrounded_by_spaces = re.compile(r'\s+[-|–|—]+\s+')

multiple_newlines = re.compile(r'((\n)\2{2,})')

MAGIC_SEQUENCE = "🇬🇧🐦✉️"

magic_sequence_regex = re.compile(MAGIC_SEQUENCE)


def unlink_govuk_escaped(message):
    return re.sub(
        govuk_not_a_link,
        r'\1' + '.\u200B' + r'\2',  # Unicode zero-width space
        message
    )


def nl2br(value):
    return re.sub(r'\n|\r', '<br>', value.strip())


def add_prefix(body, prefix=None):
    if prefix:
        return "{}: {}".format(prefix.strip(), body)
    return body


def prepend_subject(body, subject):
    return '# {}\n\n{}'.format(subject, body)


def remove_empty_lines(lines):
    return '\n'.join(filter(None, str(lines).split('\n')))


def gsm_encode(content):
    return gsm.encode(content)


def strip_html(value):
    return bleach.clean(value, tags=[], strip=True)


def escape_html(value):
    if not value:
        return value
    value = str(value).replace('<', '&lt;')
    return bleach.clean(value, tags=[], strip=False)


def strip_dvla_markup(value):
    return re.sub(dvla_markup_tags, '', value)


def unescaped_formatted_list(
    items,
    conjunction='and',
    before_each='‘',
    after_each='’',
    separator=', ',
    prefix='',
    prefix_plural=''
):
    if prefix:
        prefix += ' '
    if prefix_plural:
        prefix_plural += ' '

    if len(items) == 1:
        return '{prefix}{before_each}{items[0]}{after_each}'.format(**locals())
    elif items:
        formatted_items = ['{}{}{}'.format(before_each, item, after_each) for item in items]

        first_items = separator.join(formatted_items[:-1])
        last_item = formatted_items[-1]
        return (
            '{prefix_plural}{first_items} {conjunction} {last_item}'
        ).format(**locals())


def formatted_list(
    items,
    conjunction='and',
    before_each='‘',
    after_each='’',
    separator=', ',
    prefix='',
    prefix_plural=''
):
    return Markup(
        unescaped_formatted_list(
            [escape_html(x) for x in items],
            conjunction,
            before_each,
            after_each,
            separator,
            prefix,
            prefix_plural
        )
    )


def fix_extra_newlines_in_dvla_lists(dvla_markup):
    return dvla_markup.replace(
        '<cr><cr><cr><op>',
        '<cr><op>',
    )


def strip_pipes(value):
    return value.replace('|', '')


def remove_whitespace_before_punctuation(value):
    return re.sub(
        whitespace_before_punctuation,
        lambda match: match.group(1),
        value
    )


def make_quotes_smart(value):
    return smartypants.smartypants(
        value,
        smartypants.Attr.q | smartypants.Attr.u
    )


def replace_hyphens_with_en_dashes(value):
    return re.sub(
        hyphens_surrounded_by_spaces,
        (
            '\u00A0'  # non breaking space
            '\u2013'  # en dash
            ' '       # space
        ),
        value,
    )


def normalise_newlines(value):
    return re.sub(
        r'\r\n',
        '\n',
        value
    )


def make_markdown_take_notice_of_multiple_newlines(value):
    return re.sub(
        multiple_newlines,
        lambda match: '\n\n{}'.format(
            (MAGIC_SEQUENCE + '\n') * (len(match.group(1)) - 2)
        ),
        normalise_newlines(value)
    )


def strip_characters_inserted_to_force_newlines(value):
    return re.sub(
        magic_sequence_regex,
        '',
        value
    )


class NotifyLetterMarkdownPreviewRenderer(mistune.Renderer):

    def block_code(self, code, language=None):
        return code

    def block_quote(self, text):
        return text

    def header(self, text, level, raw=None):
        if level == 1:
            return super().header(text, 2)
        return self.paragraph(text)

    def hrule(self):
        return ""

    def paragraph(self, text):
        if text.strip():
            return '<p>{}</p>'.format(text)
        return ''

    def table(self, header, body):
        return ""

    def autolink(self, link, is_email=False):
        return '<strong>{}</strong>'.format(
            link.replace('http://', '').replace('https://', '')
        )

    def codespan(self, text):
        return text

    def double_emphasis(self, text):
        return text

    def emphasis(self, text):
        return text

    def image(self, src, title, alt_text):
        return ""

    def linebreak(self):
        return "<br/>"

    def newline(self):
        return "<br/>"

    def list_item(self, text):
        return '<li>{}</li>\n'.format(text.strip())

    def link(self, link, title, content):
        return '{}: {}'.format(content, self.autolink(link))

    def strikethrough(self, text):
        return text

    def footnote_ref(self, key, index):
        return ""

    def footnote_item(self, key, text):
        return text

    def footnotes(self, text):
        return text


class NotifyLetterMarkdownDVLARenderer(NotifyLetterMarkdownPreviewRenderer):

    def header(self, text, level, raw=None):
        if level == 1:
            return '<h2>{}<normal><cr><cr>'.format(text)
        return self.paragraph(text)

    def paragraph(self, text):
        if text.strip():
            return '{}<cr><cr>'.format(text)
        return ''

    def linebreak(self):
        return "<cr>"

    def newline(self):
        return "<cr>"

    def list(self, body, ordered=True):
        return (
            '{}'
            '{}'
            '<p>'
            '<cr>'
        ).format(
            '' if ordered else '<cr>',
            ''.join(
                '{}{}'.format(
                    '<np>' if ordered else '<op><bul><tab>',
                    line
                )
                for line in filter(None, body.split('\n'))
            ),
        )

    def list_item(self, text):
        return '{}\n'.format(text.strip())

    def link(self, link, title, content):
        return '{}: {}'.format(content, self.autolink(link))

    def autolink(self, link, is_email=False):
        return '<b>{}<normal>'.format(
            link.replace('http://', '').replace('https://', '')
        )


class NotifyEmailMarkdownRenderer(NotifyLetterMarkdownPreviewRenderer):

    def header(self, text, level, raw=None):
        if level == 1:
            return (
                '<h2 style="Margin: 0 0 20px 0; padding: 0; '
                'font-size: 27px; line-height: 35px; font-weight: bold; color: #0B0C0C;">'
                '{}'
                '</h2>'
            ).format(
                text
            )
        return self.paragraph(text)

    def list(self, body, ordered=True):
        return (
            '<ol style="Margin: 0 0 20px 0; padding: 0; list-style-type: decimal;">'
            '{}'
            '</ol>'
        ).format(
            body
        ) if ordered else (
            '<ul style="Margin: 0 0 20px 0; padding: 0; list-style-type: disc;">'
            '{}'
            '</ul>'
        ).format(
            body
        )

    def list_item(self, text):
        return (
            '<li style="Margin: 5px 0 5px 20px; padding: 0; display: list-item; font-size: 19px; '
            'line-height: 25px; color: #0B0C0C;">'
            '{}'
            '</li>'
        ).format(
            text.strip()
        )

    def paragraph(self, text):
        if text.strip():
            return (
                '<p style="Margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0B0C0C;">{}</p>'
            ).format(
                text
            )
        return ""

    def block_quote(self, text):
        return (
            '<blockquote '
            'style="Margin: 0 0 20px 0; border-left: 10px solid #BFC1C3;'
            'padding: 15px 0 0.1px 15px; font-size: 19px; line-height: 25px;"'
            '>'
            '{}'
            '</blockquote>'
        ).format(
            text
        )

    def link(self, link, title, content):
        return '{}: <a style="word-wrap: break-word;" href="{}">{}</a>'.format(content, link, link)

    def autolink(self, link, is_email=False):
        if is_email:
            return link
        return '<a style="word-wrap: break-word;" href="{}">{}</a>'.format(
            urllib.parse.quote(
                urllib.parse.unquote(link),
                safe=':/?#=&;'
            ),
            link
        )


notify_email_markdown = mistune.Markdown(
    renderer=NotifyEmailMarkdownRenderer(),
    hard_wrap=True,
    use_xhtml=False,
)
notify_letter_preview_markdown = mistune.Markdown(
    renderer=NotifyLetterMarkdownPreviewRenderer(),
    hard_wrap=True,
    use_xhtml=False,
)
notify_letter_dvla_markdown = mistune.Markdown(
    renderer=NotifyLetterMarkdownDVLARenderer(),
    hard_wrap=True,
    use_xhtml=False,
)
