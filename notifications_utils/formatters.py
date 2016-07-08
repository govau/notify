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
        r'(https?://\S+)',
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
