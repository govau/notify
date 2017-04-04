import re

from orderedset import OrderedSet
from flask import Markup

from notifications_utils.columns import Columns
from notifications_utils.formatters import unescaped_formatted_list, strip_html, escape_html


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
    placeholder_tag_no_brackets = "<span class='placeholder-no-brackets'>{}{}</span>"

    def __init__(self, content, values=None, with_brackets=True, html='strip', markdown_lists=False):
        self.content = content
        self.values = values
        self.markdown_lists = markdown_lists
        if not with_brackets:
            self.placeholder_tag = self.placeholder_tag_no_brackets
        self.sanitizer = {
            'strip': strip_html,
            'escape': escape_html,
            'passthrough': str
        }[html]

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
            return self.optional_placeholder_tag.format(
                self.sanitizer(match.group(1)),
                self.sanitizer(match.group(3))
            )
        return self.placeholder_tag.format(
            self.sanitizer(match.group(1)), self.sanitizer(match.group(3))
        )

    def replace_match(self, match):
        if match.group(2) and match.group(3) and self.values.get(match.group(1)) is not None:
            return match.group(3) if str2bool(self.values.get(match.group(1))) else ''
        if self.get_replacement(match) is not None:
            return self.get_replacement(match)
        return self.format_match(match)

    def get_replacement(self, match):

        replacement = self.values.get(match.group(1) + match.group(3))

        if isinstance(replacement, list):
            replacement = list(filter(None, replacement))
            if not replacement:
                return None
            if self.markdown_lists:
                return self.sanitizer('\n\n' + '\n'.join(
                    '* {}'.format(item) for item in replacement
                ))
            return self.sanitizer(unescaped_formatted_list(replacement, before_each='', after_each=''))

        if isinstance(replacement, bool):
            return str(replacement)

        if replacement:
            return self.sanitizer(str(replacement)) or ''

        if replacement == '':
            return ''

        return None

    @property
    def _raw_formatted(self):
        return re.sub(
            self.placeholder_pattern, self.format_match, self.sanitizer(self.content)
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
            self.placeholder_pattern, self.replace_match, self.sanitizer(self.content)
        )


def str2bool(value):
    if not value:
        return False
    return str(value).lower() in ("yes", "y", "true", "t", "1", "include", "show")
