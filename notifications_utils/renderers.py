import re
import urllib
from os import path
from jinja2 import Environment, FileSystemLoader
from notifications_utils.take import Take


email_template = Environment(loader=FileSystemLoader(
    path.dirname(path.abspath(__file__))
)).get_template('email_template.jinja2')


govuk_not_a_link = re.compile(
    r'(?<!\.|\/)(GOV)\.(UK)(?!\/|\?)',
    re.IGNORECASE
)


class SMSMessage():

    def __init__(self, prefix=None):
        self.prefix = prefix

    def __call__(self, body):
        return Take(
            body
        ).then(
            add_prefix, self.prefix
        ).as_string


class SMSPreview():

    def __init__(self, prefix=None):
        self.prefix = prefix

    def __call__(self, body):
        return Take(
            body
        ).then(
            add_prefix, self.prefix
        ).then(
            nl2br
        ).as_string


class EmailPreview():

    def __init__(self):
        pass

    def __call__(self, body):
        return Take(
            body
        ).then(
            unlink_govuk_escaped
        ).then(
            linkify
        ).then(
            nl2br
        ).as_string


class PlainTextEmail():

    def __init__(self):
        pass

    def __call__(self, body):
        return unlink_govuk_escaped(body)


class HTMLEmail():

    def __init__(self, govuk_banner=True, complete_html=True):
        self.govuk_banner = govuk_banner
        self.complete_html = complete_html

    def __call__(self, body):
        return email_template.render({
            'body': Take(
                body
            ).then(
                unlink_govuk_escaped
            ).then(
                linkify
            ).then(
                nl2br
            ).as_string,
            'govuk_banner': self.govuk_banner,
            'complete_html': self.complete_html
        })


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
