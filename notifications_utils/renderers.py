from os import path
from jinja2 import Environment, FileSystemLoader
from notifications_utils.field import Field
from notifications_utils.take import Take
from notifications_utils.formatters import (
    unlink_govuk_escaped,
    linkify,
    nl2br,
    add_prefix,
    notify_email_markdown,
    notify_letter_preview_markdown,
    prepare_newlines_for_markdown,
    prepend_subject,
    prepend_postal_address
)


email_template = Environment(loader=FileSystemLoader(
    path.dirname(path.abspath(__file__))
)).get_template('email_template.jinja2')


class PassThrough():

    def __init__(self):
        pass

    def __call__(self, body, values=None):
        return body


class SMSMessage():

    def __init__(self, prefix=None, sender=None):
        self.prefix = prefix
        self.sender = sender

    def __call__(self, body, values=None):
        return Take(
            body
        ).then(
            add_prefix, self.prefix if not self.sender else None
        ).as_string


class SMSPreview(SMSMessage):

    def __call__(self, body, values=None):
        return Take(
            SMSMessage(self.prefix, self.sender)(body)
        ).then(
            nl2br
        ).as_string


class EmailPreview(PassThrough):

    def __call__(self, body, values=None):
        return Take(
            body
        ).then(
            unlink_govuk_escaped
        ).then(
            linkify
        ).then(
            prepare_newlines_for_markdown
        ).then(
            notify_email_markdown
        ).as_string


class PlainTextEmail(PassThrough):

    def __call__(self, body, values=None):
        return unlink_govuk_escaped(body)


class HTMLEmail():

    def __init__(
        self,
        govuk_banner=True,
        complete_html=True,
        brand_logo=None,
        brand_name=None,
        brand_colour=None
    ):
        self.govuk_banner = govuk_banner
        self.complete_html = complete_html
        self.brand_logo = brand_logo
        self.brand_name = brand_name
        self.brand_colour = brand_colour and brand_colour.replace('#', '')

    def __call__(self, body, values=None):
        return email_template.render({
            'body': EmailPreview()(
                body
            ),
            'govuk_banner': self.govuk_banner,
            'complete_html': self.complete_html,
            'brand_logo': self.brand_logo,
            'brand_name': self.brand_name,
            'brand_colour': self.brand_colour
        })


class LetterPreview(PassThrough):

    address_block = '\n'.join([
        '((address line 1))',
        '((address line 2))',
        '((address line 3))',
        '((address line 4))',
        '((address line 5))',
        '((address line 6))',
        '((postcode))',
    ])

    def __init__(self, subject):
        self.subject = subject

    def __call__(self, body, values=None):
        return Take(
            body
        ).then(
            prepend_subject, self.subject
        ).then(
            prepend_postal_address, Field(self.address_block, values)
        ).then(
            prepare_newlines_for_markdown
        ).then(
            notify_letter_preview_markdown
        ).as_string
