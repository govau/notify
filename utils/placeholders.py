import re

from orderedset import OrderedSet
from flask import Markup


class Placeholders():

    def __init__(self, template):
        if not isinstance(template, str):
            raise TypeError('Template must be a string')
        self.template = str(template)
        self.pattern = r"\(\(([^\)\(]+)\)\)"  # anything that looks like ((registration number))
        self.opening_tag = "<span class='placeholder'>"
        self.closing_tag = "</span>"

    def __str__(self):
        return self.template

    def __repr__(self):
        return "Placeholders(\"{}\")".format(self.template)

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

    def replace(self, values):
        return re.sub(
            self.pattern,
            lambda match: values.get(match.group(1), ''),
            self.template
        )

    @property
    def list(self):
        return OrderedSet(re.findall(
            self.pattern, self.template
        ))

    @property
    def marked_up_list(self):
        return [
            Markup(Placeholders.opening_tag + placeholder + Placeholders.closing_tag)
            for placeholder in self.list
        ]
