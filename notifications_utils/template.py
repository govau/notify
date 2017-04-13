import math
from os import path
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from flask import Markup

from notifications_utils.columns import Columns
from notifications_utils.field import Field
from notifications_utils.formatters import (
    unlink_govuk_escaped,
    nl2br,
    add_prefix,
    notify_email_markdown,
    notify_letter_preview_markdown,
    notify_letter_dvla_markdown,
    prepare_newlines_for_markdown,
    remove_empty_lines,
    gsm_encode,
    escape_html,
    fix_extra_newlines_in_dvla_lists,
)
from notifications_utils.take import Take
from notifications_utils.template_change import TemplateChange


template_env = Environment(loader=FileSystemLoader(
    path.dirname(path.abspath(__file__))
))


class Template():

    encoding = "utf-8"

    def __init__(
        self,
        template,
        values=None,
    ):
        if not isinstance(template, dict):
            raise TypeError('Template must be a dict')
        if values is not None and not isinstance(values, dict):
            raise TypeError('Values must be a dict')
        self.id = template.get("id", None)
        self.name = template.get("name", None)
        self.content = template["content"]
        self.values = values
        self.template_type = template.get('template_type', None)
        self._template = template

    def __repr__(self):
        return "{}(\"{}\", {})".format(self.__class__.__name__, self.content, self.values)

    def __str__(self):
        return str(
            Field(self.content, self.values)
        )

    @property
    def values(self):
        if hasattr(self, '_values'):
            return self._values
        return {}

    @values.setter
    def values(self, value):
        if not value:
            self._values = {}
        else:
            placeholders = Columns.from_keys(self.placeholders)
            self._values = Columns(value).as_dict_with_keys(
                self.placeholders | set(
                    key for key in value.keys()
                    if Columns.make_key(key) not in placeholders.keys()
                )
            )

    @property
    def placeholders(self):
        return Field(self.content).placeholders

    @property
    def missing_data(self):
        return list(
            placeholder for placeholder in self.placeholders
            if self.values.get(placeholder) is None
        )

    @property
    def additional_data(self):
        return self.values.keys() - self.placeholders

    def get_raw(self, key, default=None):
        return self._template.get(key, default)

    def compare_to(self, new):
        return TemplateChange(self, new)


class SMSMessageTemplate(Template):

    def __init__(
        self,
        template,
        values=None,
        prefix=None,
        sender=None
    ):
        self.prefix = prefix
        self.sender = sender
        super().__init__(template, values)

    def __str__(self):
        return Take.as_field(
            self.content, self.values, html='passthrough'
        ).then(
            add_prefix, self.prefix
        ).then(
            gsm_encode
        ).as_string.strip()

    @property
    def prefix(self):
        return self._prefix if not self.sender else None

    @prefix.setter
    def prefix(self, value):
        self._prefix = value

    @property
    def content_count(self):
        return len((
            str(self) if self._values else gsm_encode(add_prefix(self.content.strip(), self.prefix))
        ).encode(self.encoding))

    @property
    def fragment_count(self):
        return get_sms_fragment_count(self.content_count)


class SMSPreviewTemplate(SMSMessageTemplate):

    jinja_template = template_env.get_template('sms_preview_template.jinja2')

    def __init__(
        self,
        template,
        values=None,
        prefix=None,
        sender=None,
        show_recipient=False
    ):
        self.show_recipient = show_recipient
        super().__init__(template, values, prefix, sender)

    def __str__(self):

        return Markup(self.jinja_template.render({
            'recipient': Field('((phone number))', self.values, with_brackets=False, html='escape'),
            'show_recipient': self.show_recipient,
            'body': Take.as_field(
                self.content, self.values, html='escape'
            ).then(
                add_prefix, (escape_html(self.prefix) or None) if not self.sender else None
            ).then(
                gsm_encode
            ).then(
                nl2br
            ).as_string
        }))


class WithSubjectTemplate(Template):

    def __init__(
        self,
        template,
        values=None
    ):
        self._subject = template['subject']
        super().__init__(template, values)

    @property
    def subject(self):
        return str(Field(self._subject, self.values, html='passthrough'))

    @subject.setter
    def subject(self, value):
        self._subject = value

    @property
    def placeholders(self):
        return Field(self._subject).placeholders | Field(self.content).placeholders


class PlainTextEmailTemplate(WithSubjectTemplate):

    def __str__(self):
        return Take.as_field(
            self.content, self.values, html='passthrough', markdown_lists=True
        ).then(
            unlink_govuk_escaped
        ).as_string


class HTMLEmailTemplate(WithSubjectTemplate):

    jinja_template = template_env.get_template('email_template.jinja2')

    def __init__(
        self,
        template,
        values=None,
        govuk_banner=True,
        complete_html=True,
        brand_logo=None,
        brand_name=None,
        brand_colour=None
    ):
        super().__init__(template, values)
        self.govuk_banner = govuk_banner
        self.complete_html = complete_html
        self.brand_logo = brand_logo
        self.brand_name = brand_name
        self.brand_colour = brand_colour and brand_colour.replace('#', '')

    def __str__(self):

        return self.jinja_template.render({
            'body': get_html_email_body(
                self.content, self.values
            ),
            'govuk_banner': self.govuk_banner,
            'complete_html': self.complete_html,
            'brand_logo': self.brand_logo,
            'brand_name': self.brand_name,
            'brand_colour': self.brand_colour
        })


class EmailPreviewTemplate(WithSubjectTemplate):

    jinja_template = template_env.get_template('email_preview_template.jinja2')

    def __init__(
        self,
        template,
        values=None,
        from_name=None,
        from_address=None,
        expanded=False,
        show_recipient=True
    ):
        super().__init__(template, values)
        self.from_name = from_name
        self.from_address = from_address
        self.expanded = expanded
        self.show_recipient = show_recipient

    def __str__(self):
        return Markup(self.jinja_template.render({
            'body': get_html_email_body(
                self.content, self.values
            ),
            'subject': self.subject,
            'from_name': escape_html(self.from_name),
            'from_address': self.from_address,
            'recipient': Field("((email address))", self.values, with_brackets=False),
            'expanded': self.expanded,
            'show_recipient': self.show_recipient
        }))

    @property
    def subject(self):
        return str(Field(self._subject, self.values, html='escape'))


class LetterPreviewTemplate(WithSubjectTemplate):

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

    def __init__(
        self,
        template,
        values=None,
        contact_block=None,
        admin_base_url='http://localhost:6012',
        logo_file_name='hm-government.svg',
    ):
        super().__init__(template, values)
        self.contact_block = (contact_block or '').strip()
        self.admin_base_url = admin_base_url
        self.logo_file_name = logo_file_name

    def __str__(self):
        return Markup(self.jinja_template.render({
            'admin_base_url': self.admin_base_url,
            'logo_file_name': self.logo_file_name,
            'subject': self.subject,
            'message': Take.as_field(
                self.content, self.values, html='escape', markdown_lists=True
            ).then(
                prepare_newlines_for_markdown
            ).then(
                notify_letter_preview_markdown
            ).as_string,
            'address': Take.from_field(
                Field(
                    self.address_block,
                    (
                        self.values_with_default_optional_address_lines
                        if all(Columns(self.values).get(key) for key in {
                            'address line 1',
                            'address line 2',
                            'postcode',
                        }) else self.values
                    ),
                    html='escape',
                    with_brackets=False
                )
            ).then(
                remove_empty_lines
            ).then(
                nl2br
            ).as_string,
            'contact_block': '<br/>'.join(
                line.strip()
                for line in self.contact_block.split('\n')
            ),
            'date': datetime.utcnow().strftime('%-d %B %Y')
        }))

    @property
    def subject(self):
        return str(Field(self._subject, self.values, html='escape'))

    @property
    def values_with_default_optional_address_lines(self):
        keys = Columns.from_keys(
            set(self.values.keys()) | {
                'address line 3',
                'address line 4',
                'address line 5',
                'address line 6',
            }
        ).keys()

        return {
            key: Columns(self.values).get(key) or ''
            for key in keys
        }


class LetterPDFLinkTemplate(WithSubjectTemplate):

    jinja_template = template_env.get_template('letter_preview_template.jinja2')

    def __init__(
        self,
        template,
        values=None,
        preview_url=None,
    ):
        super().__init__(template, values)
        if not preview_url:
            raise TypeError('preview_url is required')
        self.preview_url = preview_url

    def __str__(self):
        return Markup(self.jinja_template.render({
            'pdf_url': '{}.pdf'.format(self.preview_url),
            'png_url': '{}.png'.format(self.preview_url),
        }))


class LetterDVLATemplate(LetterPreviewTemplate):

    address_block = '\n'.join([
        '((address line 1))',
        '',
        '((address line 2))',
        '((address line 3))',
        '((address line 4))',
        '((address line 5))',
        '((address line 6))',
        '((postcode))'
    ])

    def __init__(
        self,
        template,
        values=None,
        numeric_id=None,
        contact_block=None,
        org_id='500',
    ):
        super().__init__(template, values, contact_block=contact_block)
        self.numeric_id = numeric_id
        self.org_id = org_id

    @property
    def numeric_id(self):
        return datetime.utcnow().strftime(
            '%Y%m%d{0:07d}'.format(self._numeric_id)
        )

    @numeric_id.setter
    def numeric_id(self, value):
        if not value:
            raise TypeError('numeric_id is required')
        if len(str(value)) > 7:
            raise TypeError('numeric_id cannot be longer than 7 digits')
        if not isinstance(value, int):
            raise TypeError('numeric_id must be an integer')
        self._numeric_id = int(value)

    def __str__(self):

        OTT = '140'
        ORG_ID = self.org_id
        ORG_NOTIFICATION_TYPE = '001'
        ORG_NAME = ''
        NOTIFICATION_ID = self.numeric_id
        NOTIFICATION_DATE = ''
        CUSTOMER_REFERENCE = ''
        ADDITIONAL_LINE_1, \
            ADDITIONAL_LINE_2, \
            ADDITIONAL_LINE_3, \
            ADDITIONAL_LINE_4, \
            ADDITIONAL_LINE_5, \
            ADDITIONAL_LINE_6, \
            ADDITIONAL_LINE_7, \
            ADDITIONAL_LINE_8, \
            ADDITIONAL_LINE_9, \
            ADDITIONAL_LINE_10 = [
                line.strip()
                for line in
                (self.contact_block.split('\n') + ([''] * 10))
            ][:10]
        TO_NAME_1,\
            _,\
            TO_ADDRESS_LINE_1,\
            TO_ADDRESS_LINE_2,\
            TO_ADDRESS_LINE_3,\
            TO_ADDRESS_LINE_4,\
            TO_ADDRESS_LINE_5,\
            TO_POST_CODE, = str(Field(
                self.address_block,
                self.values_with_default_optional_address_lines,
            )).split('\n')
        TO_NAME_2 = ''
        RETURN_NAME = ''
        RETURN_ADDRESS_LINE_1 = ''
        RETURN_ADDRESS_LINE_2 = ''
        RETURN_ADDRESS_LINE_3 = ''
        RETURN_ADDRESS_LINE_4 = ''
        RETURN_ADDRESS_LINE_5 = ''
        RETURN_POST_CODE = ''
        SUBJECT_LINE = ''
        NOTIFICATION_BODY = (
            '{}<cr><cr>'
            '<h1>{}<normal><cr><cr>'
            '{}'
        ).format(
            datetime.utcnow().strftime('%-d %B %Y'),
            str(Field(self.subject, self.values)),
            Take.as_field(
                self.content, self.values, markdown_lists=True
            ).then(
                prepare_newlines_for_markdown
            ).then(
                notify_letter_dvla_markdown
            ).then(
                fix_extra_newlines_in_dvla_lists
            ).as_string
        )

        return '|'.join(line.replace('|', '') for line in [
            OTT,
            ORG_ID,
            ORG_NOTIFICATION_TYPE,
            ORG_NAME,
            NOTIFICATION_ID,
            NOTIFICATION_DATE,
            CUSTOMER_REFERENCE,
            ADDITIONAL_LINE_1,
            ADDITIONAL_LINE_2,
            ADDITIONAL_LINE_3,
            ADDITIONAL_LINE_4,
            ADDITIONAL_LINE_5,
            ADDITIONAL_LINE_6,
            ADDITIONAL_LINE_7,
            ADDITIONAL_LINE_8,
            ADDITIONAL_LINE_9,
            ADDITIONAL_LINE_10,
            TO_NAME_1,
            TO_NAME_2,
            TO_ADDRESS_LINE_1,
            TO_ADDRESS_LINE_2,
            TO_ADDRESS_LINE_3,
            TO_ADDRESS_LINE_4,
            TO_ADDRESS_LINE_5,
            TO_POST_CODE,
            RETURN_NAME,
            RETURN_ADDRESS_LINE_1,
            RETURN_ADDRESS_LINE_2,
            RETURN_ADDRESS_LINE_3,
            RETURN_ADDRESS_LINE_4,
            RETURN_ADDRESS_LINE_5,
            RETURN_POST_CODE,
            SUBJECT_LINE,
            NOTIFICATION_BODY,
        ])


class NeededByTemplateError(Exception):
    def __init__(self, keys):
        super(NeededByTemplateError, self).__init__(", ".join(keys))


class NoPlaceholderForDataError(Exception):
    def __init__(self, keys):
        super(NoPlaceholderForDataError, self).__init__(", ".join(keys))


def get_sms_fragment_count(character_count):
    return 1 if character_count <= 160 else math.ceil(float(character_count) / 153)


def get_html_email_body(template_content, template_values):

    return Take.as_field(
        template_content, template_values, html='escape', markdown_lists=True
    ).then(
        unlink_govuk_escaped
    ).then(
        prepare_newlines_for_markdown
    ).then(
        notify_email_markdown
    ).as_string
