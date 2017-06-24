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
    strip_dvla_markup,
    strip_pipes,
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
        return Markup(
            Field(self.content, self.values, html='escape')
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
        show_recipient=False,
        downgrade_non_gsm_characters=True,
    ):
        self.show_recipient = show_recipient
        self.downgrade_non_gsm_characters = downgrade_non_gsm_characters
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
                gsm_encode if self.downgrade_non_gsm_characters else str
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
        return Markup(Field(self._subject, self.values, html='escape'))

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

    @property
    def subject(self):
        return Markup(Field(self._subject, self.values, html='passthrough', redact_missing=self.redact_missing))


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
        self.contact_block = (contact_block or '').strip()
        super().__init__(template, values)
        self.admin_base_url = admin_base_url
        self.logo_file_name = logo_file_name

    def __str__(self):
        return Markup(self.jinja_template.render({
            'admin_base_url': self.admin_base_url,
            'logo_file_name': self.logo_file_name,
            'subject': self.subject,
            'message': Take.as_field(
                strip_dvla_markup(self.content), self.values, html='escape', markdown_lists=True
            ).then(
                strip_pipes
            ).then(
                prepare_newlines_for_markdown
            ).then(
                notify_letter_preview_markdown
            ).as_string,
            'address': Take.as_field(
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
            ).then(
                strip_pipes
            ).then(
                remove_empty_lines
            ).then(
                nl2br
            ).as_string,
            'contact_block': Take.as_field(
                '\n'.join(
                    line.strip()
                    for line in self.contact_block.split('\n')
                ),
                self.values,
                html='escape',
            ).then(
                nl2br
            ).then(
                strip_pipes
            ).as_string,
            'date': datetime.utcnow().strftime('%-d %B %Y')
        }))

    @property
    def subject(self):
        return Take.as_field(
            self._subject, self.values, html='escape'
        ).then(
            strip_pipes
        ).then(
            strip_dvla_markup
        ).as_string

    @property
    def placeholders(self):
        return super().placeholders | Field(self.contact_block).placeholders

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


class LetterImageTemplate(LetterPreviewTemplate):

    jinja_template = template_env.get_template('letter_image_template.jinja2')

    def __init__(
        self,
        template,
        values=None,
        image_url=None,
        page_count=None,
        contact_block=None,
    ):
        super().__init__(template, values, contact_block=contact_block)
        if not image_url:
            raise TypeError('image_url is required')
        if not page_count:
            raise TypeError('page_count is required')
        self.image_url = image_url
        self.page_count = int(page_count)

    def __str__(self):
        return Markup(self.jinja_template.render({
            'image_url': self.image_url,
            'page_numbers': range(1, self.page_count + 1),
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
        notification_reference=None,
        contact_block=None,
        org_id='500',
    ):
        super().__init__(template, values, contact_block=contact_block)
        self.notification_reference = notification_reference
        self.org_id = org_id

    @property
    def notification_reference(self):
        return self._notification_reference

    @notification_reference.setter
    def notification_reference(self, value):
        if not value:
            raise TypeError('notification_reference is required')
        if len(str(value)) > 16:
            raise TypeError('notification_reference cannot be longer than 16 chars')
        self._notification_reference = str(value)

    @property
    def subject(self):
        return str(Field(self._subject, self.values, html='strip_dvla_markup'))

    def __str__(self):

        OTT = '140'
        ORG_ID = self.org_id
        ORG_NOTIFICATION_TYPE = '001'
        ORG_NAME = ''
        NOTIFICATION_ID = self.notification_reference
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
                ((
                    Take.as_field(self.contact_block, self.values, html='strip_dvla_markup')
                ).as_string.split('\n') + ([''] * 10))
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
            self.subject,
            Take.as_field(
                self.content, self.values, markdown_lists=True, html='strip_dvla_markup'
            ).then(
                prepare_newlines_for_markdown
            ).then(
                notify_letter_dvla_markdown
            ).then(
                fix_extra_newlines_in_dvla_lists
            ).as_string
        )

        return '|'.join(strip_pipes(line) for line in [
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
