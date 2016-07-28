import re
import urllib
import mistune


mistune._block_quote_leading_pattern = re.compile(r'^ *\^ ?', flags=re.M)
mistune.BlockGrammar.block_quote = re.compile(r'^( *\^[^\n]+(\n[^\n]+)*\n*)+')

govuk_not_a_link = re.compile(
    r'(?<!\.|\/)(GOV)\.(UK)(?!\/|\?)',
    re.IGNORECASE
)


def unlink_govuk_escaped(message):
    return re.sub(
        govuk_not_a_link,
        r'\1' + '.\u200B' + r'\2',  # Unicode zero-width space
        message
    )


def linkify(text):
    return re.sub(
        #             url is anything without whitespace, >, or <
        r'(https?:\/\/[^\s\<\>]+)($|\s)',
        lambda match: '<a href="{}">{}</a>{}'.format(
            urllib.parse.quote(
                urllib.parse.unquote(match.group(1)),
                safe=':/?#=&'
            ),
            match.group(1),
            match.group(2)
        ),
        text
    )


def nl2br(value):
    return re.sub(r'\n|\r', '<br>', value.strip())


def add_prefix(body, prefix=None):
    if prefix:
        return "{}: {}".format(prefix.strip(), body)
    return body


class NotifyMarkdownRenderer(mistune.Renderer):

    def block_code(self, code, language=None):
        return code

    def block_quote(self, text):
        return (
            '<blockquote '
            'style="margin: 0 0 20px 0; border-left: 10px solid #BFC1C3;'
            'padding: 15px 0 0.1px 15px; font-size: 19px; line-height: 25px;"'
            '>'
            '{}'
            '</blockquote>'
        ).format(
            text
        )

    def header(self, text, level, raw=None):
        if level == 1:
            return (
                '<h2 style="margin: 0 0 20px 0; padding: 0; font-size: 27px; line-height: 35px; font-weight: bold">'
                '{}'
                '</h2>'
            ).format(
                text
            )
        return self.paragraph(text)

    def hrule(self):
        return ""

    def list(self, body, ordered=True):
        return (
            '<ol style="margin: 0 0 20px 0; padding: 0 0 0 20px; list-style-type: decimal;">'
            '{}'
            '</ol>'
        ).format(
            body
        ) if ordered else (
            '<ul style="margin: 0 0 20px 0; padding: 0 0 0 20px; list-style-type: disc;">'
            '{}'
            '</ul>'
        ).format(
            body
        )

    def list_item(self, text):
        return (
            '<li style="margin: 5px 0; padding: 0; display: list-item; font-size: 19px; line-height: 25px;">'
            '{}'
            '</li>'
        ).format(
            text
        )

    def paragraph(self, text):
        if text.strip():
            return (
                '<p style="margin: 0 0 20px 0; font-size: 19px; line-height: 25px;">{}</p>'
            ).format(
                text
            )
        return ""

    def table(self, header, body):
        return ""

    def autolink(self, link, is_email=False):
        return link

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

    def link(self, link, title, content):
        return '{}: {}'.format(content, link)

    def strikethrough(self, text):
        return text

    def footnote_ref(self, key, index):
        return ""

    def footnote_item(self, key, text):
        return text

    def footnotes(self, text):
        return text


notify_markdown = mistune.Markdown(renderer=NotifyMarkdownRenderer())
