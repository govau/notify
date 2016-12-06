from os import path
from jinja2 import Environment, FileSystemLoader
from flask import Markup
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
    remove_empty_lines
)

template_env = Environment(loader=FileSystemLoader(
    path.dirname(path.abspath(__file__))
))


class PassThrough():

    def __init__(self):
        pass

    def __call__(self, template, values=None):
        return str(
            Field(template['content'], template.get('values', {}))
        )


class SMSMessage():

    def __init__(self, prefix=None, sender=None):
        self.prefix = prefix
        self.sender = sender

    def __call__(self, template):
        return Take.from_field(
            Field(template['content'], template.get('values', {}))
        ).then(
            add_prefix, self.prefix if not self.sender else None
        ).as_string.strip()


class SMSPreview(SMSMessage):

    jinja_template = template_env.get_template('sms_preview_template.jinja2')

    def __init__(self, prefix=None, sender=None, show_recipient=True):
        self.prefix = prefix
        self.sender = sender
        self.show_recipient = show_recipient

    def __call__(self, template):
        return Markup(self.jinja_template.render({
            'recipient': Field('((phone number))', template.get('values', {}), with_brackets=False),
            'show_recipient': self.show_recipient,
            'body': Take(
                SMSMessage(self.prefix, self.sender)(template)
            ).then(
                nl2br
            ).as_string
        }))


class EmailBody(PassThrough):

    def __call__(self, template):
        return Take.from_field(
            Field(template['content'], template.get('values', {}))
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

    def __call__(self, template):
        return Take.from_field(
            Field(template['content'], template.get('values', {}))
        ).then(
            unlink_govuk_escaped
        ).as_string


class HTMLEmail():

    jinja_template = template_env.get_template('email_template.jinja2')

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

    def __call__(self, template):
        return self.jinja_template.render({
            'body': EmailBody()(
                template
            ),
            'govuk_banner': self.govuk_banner,
            'complete_html': self.complete_html,
            'brand_logo': self.brand_logo,
            'brand_name': self.brand_name,
            'brand_colour': self.brand_colour
        })


class EmailPreview(PassThrough):

    jinja_template = template_env.get_template('email_preview_template.jinja2')

    def __init__(
        self,
        from_name=None,
        from_address=None,
        expanded=False,
        show_recipient=True
    ):
        self.from_name = from_name
        self.from_address = from_address
        self.expanded = expanded
        self.show_recipient = show_recipient

    def __call__(self, template):
        return Markup(self.jinja_template.render({
            'body': EmailBody()(
                template
            ),
            'subject': template['subject'],
            'from_name': self.from_name,
            'from_address': self.from_address,
            'recipient': Field("((email address))", template.get('values', {}), with_brackets=False),
            'expanded': self.expanded,
            'show_recipient': self.show_recipient
        }))


class LetterPreview(PassThrough):

    jinja_template = template_env.get_template('letter_pdf_template.jinja2')

    address_block = '\n'.join([
        '((address line 1))',
        '((address line 2))',
        '((address line 3))',
        '((address line 4))',
        '((address line 5))',
        '((address line 6))',
        '((postcode))',
    ])

    def __call__(self, template):
        return Markup(self.jinja_template.render({
            'message': Take.from_field(
                Field(template['content'], template.get('values', {}))
            ).then(
                prepend_subject, Field(template['subject'], template['values'])
            ).then(
                prepare_newlines_for_markdown
            ).then(
                notify_letter_preview_markdown
            ).as_string,
            'address': Take.from_field(
                Field(self.address_block, template.get('values', {}), with_brackets=False)
            ).then(
                remove_empty_lines
            ).then(
                nl2br
            ).as_string
        }))


class LetterPDFLink(PassThrough):

    jinja_template = template_env.get_template('letter_preview_template.jinja2')

    def __init__(self, service_id):
        self.service_id = service_id

    def __call__(self, template):
        return Markup(self.jinja_template.render({
            'service_id': self.service_id,
            'template_id': template['id']
        }))
