import re
import math
import bleach

from orderedset import OrderedSet
from flask import Markup

from notifications_utils.columns import Columns
from notifications_utils.renderers import HTMLEmail, SMSPreview, EmailPreview, LetterPreview
from notifications_utils.field import Field


class Template():

    encoding = "utf-8"

    def __init__(
        self,
        template,
        values=None,
        drop_values=(),
        prefix=None,
        sms_sender=None,
        content_character_limit=None,
        renderer=None
    ):
        if not isinstance(template, dict):
            raise TypeError('Template must be a dict')
        if values is not None and not isinstance(values, dict):
            raise TypeError('Values must be a dict')
        if prefix is not None and not isinstance(prefix, str):
            raise TypeError('Prefix must be a string')
        self.id = template.get("id", None)
        self.name = template.get("name", None)
        self.content = template["content"]
        self.subject = template.get('subject', None)
        self.values = values
        self.template_type = template.get('template_type', None)
        for value in drop_values:
            self._values.pop(value, None)
        self.content_character_limit = content_character_limit
        self._template = template
        self._prefix = prefix
        self._sms_sender = sms_sender
        self.renderer = renderer

    def __repr__(self):
        return "{}(\"{}\", {})".format(self.__class__.__name__, self.content, self.values)  # TODO: more real

    def to_dict(self):
        return {
            key: getattr(self, key)
            for key in ['content', 'subject', 'values']
        }

    @property
    def values(self):
        return self._values

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
    def renderer(self):
        return self._renderer

    @renderer.setter
    def renderer(self, value):
        if value:
            self._renderer = value
        elif self.template_type == 'sms':
            self._renderer = SMSPreview(
                prefix=self._prefix,
                sender=self._sms_sender
            )
        elif self.template_type == 'letter':
            self._renderer = LetterPreview()
        elif self.template_type == 'email' or not self.template_type:
            self._renderer = EmailPreview()

    @property
    def rendered(self):
        return self.renderer(self.to_dict())

    @property
    def placeholders(self):
        return Field(self.subject or '').placeholders | Field(self.content).placeholders

    @property
    def content_count(self):
        return len(self.rendered.encode(self.encoding))

    @property
    def sms_fragment_count(self):
        if self.template_type != 'sms':
            raise TypeError("The template needs to have a template type of 'sms'")
        return get_sms_fragment_count(self.content_count)

    @property
    def content_too_long(self):
        return (
            self.content_character_limit is not None and
            self.content_count > self.content_character_limit
        )

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


class NeededByTemplateError(Exception):
    def __init__(self, keys):
        super(NeededByTemplateError, self).__init__(", ".join(keys))


class NoPlaceholderForDataError(Exception):
    def __init__(self, keys):
        super(NoPlaceholderForDataError, self).__init__(", ".join(keys))


class TemplateChange():

    def __init__(self, old_template, new_template):
        self.old_placeholders = Columns.from_keys(old_template.placeholders)
        self.new_placeholders = Columns.from_keys(new_template.placeholders)

    @property
    def has_different_placeholders(self):
        return bool(self.new_placeholders.keys() ^ self.old_placeholders.keys())

    @property
    def placeholders_added(self):
        return set(
            self.new_placeholders.get(key)
            for key in self.new_placeholders.keys() - self.old_placeholders.keys()
        )

    @property
    def placeholders_removed(self):
        return set(
            self.old_placeholders.get(key)
            for key in self.old_placeholders.keys() - self.new_placeholders.keys()
        )


def get_sms_fragment_count(character_count):
    return 1 if character_count <= 160 else math.ceil(float(character_count) / 153)
