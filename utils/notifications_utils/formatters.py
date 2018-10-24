import re
import urllib

import mistune
import bleach
from itertools import count
from flask import Markup
from notifications_utils import gsm
import smartypants

mistune._block_quote_leading_pattern = re.compile(r'^ *\^ ?', flags=re.M)
mistune.BlockGrammar.block_quote = re.compile(r'^( *\^[^\n]+(\n[^\n]+)*\n*)+')

govau_not_a_link = re.compile(
    r'(?<!\.|\/)(GOV)\.(AU)(?!\/|\?)',
    re.IGNORECASE
)

dvla_markup_tags = re.compile(
    str('|'.join('\<{}\>'.format(tag) for tag in {
        'cr', 'h1', 'h2', 'p', 'normal', 'op', 'np', 'bul', 'tab'
    })),
    re.IGNORECASE
)

smartypants.tags_to_skip = smartypants.tags_to_skip + ['a']

whitespace_before_punctuation = re.compile(r'[ \t]+([,|\.])')

hyphens_surrounded_by_spaces = re.compile(r'\s+[-|–|—]{1,3}\s+')

multiple_newlines = re.compile(r'((\n)\2{2,})')

MAGIC_SEQUENCE = "🇬🇧🐦✉️"

magic_sequence_regex = re.compile(MAGIC_SEQUENCE)


def unlink_govau_escaped(message):
    return re.sub(
        govau_not_a_link,
        r'\1' + '.\u200B' + r'\2',  # Unicode zero-width space
        message
    )


def nl2br(value):
    return re.sub(r'\n|\r', '<br>', value.strip())


def nl2li(value):
    return '<ul><li>{}</li></ul>'.format('</li><li>'.join(
        value.strip().split('\n')
    ))


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
            ' '       # space
            '\u2013'  # en dash
            ' '       # space
        ),
        value,
    )


def replace_hyphens_with_non_breaking_hyphens(value):
    return value.replace(
        '-',
        '\u2011',  # non-breaking hyphen
    )


def normalise_newlines(value):
    return '\n'.join(value.splitlines())


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


def strip_leading_whitespace(value):
    return value.lstrip()


def add_trailing_newline(value):
    return '{}\n'.format(value)


def tweak_dvla_list_markup(value):
    return value.replace('<cr><cr><np>', '<cr><np>').replace('<p><cr><p><cr>', '<p><cr>')


def remove_trailing_linebreak(value):

    block_linebreak = NotifyLetterMarkdownPreviewRenderer.block_linebreak(None)

    if value.endswith(block_linebreak):
        return remove_trailing_linebreak(
            value[:(
                -1 * len(block_linebreak)
            )].rstrip()
        )
    else:
        return value


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
            return '{}{}'.format(text, self.block_linebreak())
        return ''

    def table(self, header, body):
        return ""

    def autolink(self, link, is_email=False):
        return '<strong>{}</strong>'.format(
            link.replace('http://', '').replace('https://', '')
        )

    def codespan(self, text):
        return text

    def emphasis(self, text):
        return text

    def image(self, src, title, alt_text):
        return ""

    def block_linebreak(self):
        return "<div class='linebreak-block'>&nbsp;</div>"

    def linebreak(self):
        return "<div class='linebreak'>&nbsp;</div>"

    def newline(self):
        return self.linebreak()

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


class NotifyEmailMarkdownRenderer(mistune.Renderer):

    def table(self, header, body):
        return ""

    def image(self, src, title, alt_text):
        return ""

    def block_linebreak(self):
        return "<div class='linebreak-block'>&nbsp;</div>"

    def newline(self):
        return self.linebreak()

    def strikethrough(self, text):
        return text

    def footnote_ref(self, key, index):
        return ""

    def footnote_item(self, key, text):
        return text

    def footnotes(self, text):
        return text

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

    def hrule(self):
        return (
            '<hr style="border: 0; height: 1px; background: #BFC1C3; Margin: 30px 0 30px 0;">'
        )

    def linebreak(self):
        return "<br/>"

    def list(self, body, ordered=True):
        return (
            '<table role="presentation" style="padding: 0 0 20px 0;">'
            '<tr>'
            '<td style="font-family: Helvetica, Arial, sans-serif;">'
            '<ol style="Margin: 0 0 0 20px; padding: 0; list-style-type: decimal;">'
            '{}'
            '</ol>'
            '</td>'
            '</tr>'
            '</table>'
        ).format(
            body
        ) if ordered else (
            '<table role="presentation" style="padding: 0 0 20px 0;">'
            '<tr>'
            '<td style="font-family: Helvetica, Arial, sans-serif;">'
            '<ul style="Margin: 0 0 0 20px; padding: 0; list-style-type: disc;">'
            '{}'
            '</ul>'
            '</td>'
            '</tr>'
            '</table>'
        ).format(
            body
        )

    def list_item(self, text):
        return (
            '<li style="Margin: 5px 0 5px; padding: 0 0 0 5px; font-size: 19px;'
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
        return (
            '<a style="word-wrap: break-word;"{}{}>{}</a>'
        ).format(
            ' href="{}"'.format(link),
            ' title="{}"'.format(title) if title else "",
            content,
        )

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

    def emphasis(self, text):
        return '*{}*'.format(text)


class NotifyPlainTextEmailMarkdownRenderer(mistune.Renderer):

    COLUMN_WIDTH = 65

    def block_code(self, code, language=None):
        return code

    def table(self, header, body):
        return ""

    def codespan(self, text):
        return text

    def emphasis(self, text):
        return '*{}*'.format(text)

    def image(self, src, title, alt_text):
        return ""

    def block_linebreak(self):
        return "<div class='linebreak-block'>&nbsp;</div>"

    def newline(self):
        return self.linebreak()

    def strikethrough(self, text):
        return text

    def footnote_ref(self, key, index):
        return ""

    def footnote_item(self, key, text):
        return text

    def footnotes(self, text):
        return text

    def header(self, text, level, raw=None):
        if level == 1:
            return ''.join((
                self.linebreak() * 3,
                text,
                self.linebreak(),
                '-' * self.COLUMN_WIDTH,
            ))
        return self.paragraph(text)

    def hrule(self):
        return self.paragraph(
            '=' * self.COLUMN_WIDTH
        )

    def linebreak(self):
        return '\n'

    def list(self, body, ordered=True):

        def _get_list_marker():
            decimal = count(1)
            return lambda _: '{}.'.format(next(decimal)) if ordered else '•'

        return ''.join((
            self.linebreak(),
            re.sub(
                magic_sequence_regex,
                _get_list_marker(),
                body,
            ),
        ))

    def list_item(self, text):
        return ''.join((
            self.linebreak(),
            MAGIC_SEQUENCE,
            ' ',
            text.strip(),
        ))

    def paragraph(self, text):
        if text.strip():
            return ''.join((
                self.linebreak() * 2,
                text,
            ))
        return ""

    def block_quote(self, text):
        return text

    def link(self, link, title, content):
        return ''.join((
            content,
            ' ({})'.format(title) if title else '',
            ': ',
            link,
        ))

    def autolink(self, link, is_email=False):
        return link

    def double_emphasis(self, text):
        return '**{}**'.format(text)


notify_email_markdown = mistune.Markdown(
    renderer=NotifyEmailMarkdownRenderer(),
    hard_wrap=True,
    use_xhtml=False,
)
notify_plain_text_email_markdown = mistune.Markdown(
    renderer=NotifyPlainTextEmailMarkdownRenderer(),
    hard_wrap=True,
)
notify_letter_preview_markdown = mistune.Markdown(
    renderer=NotifyLetterMarkdownPreviewRenderer(),
    hard_wrap=True,
    use_xhtml=False,
)
