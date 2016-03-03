import re

from orderedset import OrderedSet
from flask import Markup


class Template():

    placeholder_pattern = r"\(\(([^\)\(]+)\)\)"  # anything that looks like ((registration number))
    placeholder_opening_tag = "<span class='placeholder'>"
    placeholder_closing_tag = "</span>"

    def __init__(self, template, values=None, drop_values=(), prefix=None):
        if not isinstance(template, dict):
            raise TypeError('Template must be a dict')
        if values is not None and not isinstance(values, dict):
            raise TypeError('Values must be a dict')
        if prefix is not None and not isinstance(prefix, str):
            raise TypeError('Prefix must be a string')
        self.id = template.get("id", None)
        self.name = template.get("name", None)
        self.content = template["content"]
        self.values = (values or {}).copy()
        self.template_type = template.get('template_type', None)
        self.subject = template.get('subject', None)
        for value in drop_values:
            self.values.pop(value, None)
        self.prefix = prefix

    def __str__(self):
        if self.values:
            return self.replaced
        return self.content

    def __repr__(self):
        return "{}(\"{}\", {})".format(self.__class__.__name__, self.content, self.values)  # TODO: more real

    @property
    def formatted(self):
        return self.__add_prefix(self.__nl2br(re.sub(
            Template.placeholder_pattern,
            lambda match: Template.placeholder_opening_tag + match.group(1) + Template.placeholder_closing_tag,
            self.content
        )))

    @property
    def formatted_as_markup(self):
        return Markup(self.formatted)

    @property
    def placeholders(self):
        return OrderedSet(re.findall(
            Template.placeholder_pattern, self.content
        ))

    @property
    def placeholders_as_markup(self):
        return [
            Markup(Template.placeholder_opening_tag + placeholder + Template.placeholder_closing_tag)
            for placeholder in self.placeholders
        ]

    @property
    def replaced(self):
        if self.missing_data:
            raise NeededByTemplateError(self.missing_data)
        if self.additional_data:
            raise NoPlaceholderForDataError(self.additional_data)
        return self.__add_prefix(re.sub(
            Template.placeholder_pattern,
            lambda match: self.values.get(match.group(1)),
            self.content
        ))

    @property
    def missing_data(self):
        return self.placeholders - self.values.keys()

    @property
    def additional_data(self):
        return self.values.keys() - self.placeholders

    def __add_prefix(self, output):
        if self.prefix:
            return "{}: {}".format(self.prefix.strip(), output)
        return output

    def __nl2br(self, value):
        return re.sub(r'\n|\r', '<br>', value.strip())


class NeededByTemplateError(Exception):
    def __init__(self, keys):
        super(NeededByTemplateError, self).__init__(", ".join(keys))


class NoPlaceholderForDataError(Exception):
    def __init__(self, keys):
        super(NoPlaceholderForDataError, self).__init__(", ".join(keys))
