from os import path
from jinja2 import Environment, FileSystemLoader
from notifications_utils.take import Take
from notifications_utils.formatters import (
    unlink_govuk_escaped,
    linkify,
    nl2br,
    add_prefix,
    markup_headings,
    markup_lists,
    markup_blockquotes
)


email_template = Environment(loader=FileSystemLoader(
    path.dirname(path.abspath(__file__))
)).get_template('email_template.jinja2')


class PassThrough():

    def __init__(self):
        pass

    def __call__(self, body):
        return body


class SMSMessage():

    def __init__(self, prefix=None):
        self.prefix = prefix

    def __call__(self, body):
        return Take(
            body
        ).then(
            add_prefix, self.prefix
        ).as_string


class SMSPreview(SMSMessage):

    def __call__(self, body):
        return Take(
            body
        ).then(
            add_prefix, self.prefix
        ).then(
            nl2br
        ).as_string


class EmailPreview(PassThrough):

    def __call__(self, body):
        return Take(
            body
        ).then(
            markup_headings
        ).then(
            markup_lists
        ).then(
            markup_blockquotes
        ).then(
            unlink_govuk_escaped
        ).then(
            linkify
        ).then(
            nl2br
        ).as_string


class PlainTextEmail(PassThrough):

    def __call__(self, body):
        return unlink_govuk_escaped(body)


class HTMLEmail():

    def __init__(self, govuk_banner=True, complete_html=True):
        self.govuk_banner = govuk_banner
        self.complete_html = complete_html

    def __call__(self, body):
        return email_template.render({
            'body': EmailPreview()(
                body
            ),
            'govuk_banner': self.govuk_banner,
            'complete_html': self.complete_html
        })
