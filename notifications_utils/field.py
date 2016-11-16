import re
import bleach

from orderedset import OrderedSet
from flask import Markup

from notifications_utils.columns import Columns


class Field():

    placeholder_pattern = re.compile(
        '\(\('            # opening ((
        '([^\(\)\?]+)'    # 1. name of placeholder, eg ‘registration number’
        '(\?\?)?'         # 2. optional ??
        '([^\)\(]*)'      # 3. optional text to display if the placeholder’s value is True
        '\)\)'            # closing ))
    )
    placeholder_tag = "<span class='placeholder'>(({}{}))</span>"
    optional_placeholder_tag = "<span class='placeholder-conditional'>(({}??</span>{}))"

    def __init__(self, content, values=None):
        self.content = content
        self.values = values

    def __str__(self):
        if self.values:
            return self.replaced
        return self.formatted

    def __repr__(self):
        return "{}(\"{}\", {})".format(self.__class__.__name__, self.content, self.values)  # TODO: more real

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, value):
        self._values = Columns(value) if value else {}

    def get_match(self, match):
        if match[1] and match[2]:
            return match[0]
        return match[0] + match[2]

    def format_match(self, match):
        if match.group(2) and match.group(3):
            return self.optional_placeholder_tag.format(match.group(1), match.group(3))
        return self.placeholder_tag.format(match.group(1), match.group(3))

    def replace_match(self, match):
        if match.group(2) and match.group(3):
            return strip_html(match.group(3)) if str2bool(self.values.get(match.group(1))) else ''
        return strip_html(self.values.get(match.group(1) + match.group(3)))

    @property
    def _raw_formatted(self):
        return re.sub(
            self.placeholder_pattern, self.format_match, self.content
        )

    @property
    def formatted(self):
        return Markup(self._raw_formatted)

    @property
    def placeholders(self):
        return OrderedSet(
            self.get_match(match) for match in re.findall(
                self.placeholder_pattern, self.content
            )
        )

    @property
    def replaced(self):
        return re.sub(
            self.placeholder_pattern, self.replace_match, self.content
        )


def strip_html(value):
    return bleach.clean(value, tags=[], strip=True)


def str2bool(value):
    if not value:
        return False
    return str(value).lower() in ("yes", "y", "true", "t", "1", "include", "show")
