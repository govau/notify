import re
import urllib


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
        lambda match: '<a href="{}">{}</a>'.format(
            urllib.parse.quote(
                urllib.parse.unquote(match.group(1)),
                safe=':/?#=&'
            ),
            match.group(1)
        ),
        text
    )


def nl2br(value):
    return re.sub(r'\n|\r', '<br>', value.strip())


def add_prefix(body, prefix=None):
    if prefix:
        return "{}: {}".format(prefix.strip(), body)
    return body


def markup_headings(body):
    return re.sub(
        r'^\#\s*(.+)\n',
        lambda match: (
            '<h2 style="margin: 10px 0 0 0; padding: 0; font-size: 27px; font-weight: bold">'
            '{}'
            '</h2>'
        ).format(
            match.group(1)
        ),
        body,
        flags=re.MULTILINE
    )


def markup_lists(body):
    return re.sub(
        r'^\*\s*(.+)$\n',
        lambda match: (
            '<li style="margin: 5px 0; display: list-item; list-style-type: disc; font-size: 19px;">'
            '{}'
            '</li>'
        ).format(match.group(1)),
        body,
        flags=re.MULTILINE
    )


def markup_blockquotes(body):
    return re.sub(
        r'^\^\s*(.+)$\n',
        lambda match: (
            '<blockquote style="margin: 0; border-left: 10px solid #BFC1C3; padding: 0 0 0 15px; font-size: 19px;">'
            '{}'
            '</blockquote>'
        ).format(match.group(1)),
        body,
        flags=re.MULTILINE
    )
