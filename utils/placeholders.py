import re

from orderedset import OrderedSet
from flask import Markup


class Placeholders():

    pattern = r"\(\(([^\)\(]+)\)\)"  # anything that looks like ((registration number))
    opening_tag = "<span class='placeholder'>"
    closing_tag = "</span>"

    def __init__(self, template, values=None):
        if not isinstance(template, str):
            raise TypeError('Template must be a string')
        if values is not None and not isinstance(values, dict):
            raise TypeError('Values must be a dict')
        self.template = template
        self.values = values or {}

    def __str__(self):
        if self.values:
            return self.replaced
        else:
            return self.template

    def __repr__(self):
        return "{}(\"{}\", {})".format(self.__class__.__name__, self.template, self.values)

    @property
    def formatted(self):
        return re.sub(
            Placeholders.pattern,
            lambda match: Placeholders.opening_tag + match.group(1) + Placeholders.closing_tag,
            self.template
        )

    @property
    def formatted_as_markup(self):
        return Markup(self.formatted)

    @property
    def list(self):
        return OrderedSet(re.findall(
            Placeholders.pattern, self.template
        ))

    @property
    def marked_up_list(self):
        return [
            Markup(Placeholders.opening_tag + placeholder + Placeholders.closing_tag)
            for placeholder in self.list
        ]

    @property
    def replaced(self):
        if self.missing_data:
            raise PlaceholderError("Needed by template", self.missing_data)
        if self.additional_data:
            raise PlaceholderError("Not in template", self.additional_data)
        return re.sub(
            Placeholders.pattern,
            lambda match: self.values.get(match.group(1)),
            self.template
        )

    @property
    def missing_data(self):
        return self.list - self.values.keys()

    @property
    def additional_data(self):
        return self.values.keys() - self.list


class PlaceholderError(Exception):

    def __init__(self, error, keys):
        super(PlaceholderError, self).__init__("{}: {}".format(error, ", ".join(keys)))
