import re


class Placeholders():

    def __init__(self, template):
        if not isinstance(template, str):
            raise TypeError('Template must be a string')
        self.template = str(template)
        self.pattern = r"\(\(([^\)\(]+)\)\)"  # anything that looks like ((registration number))
        self.opening_tag = "<span class='placeholder'>"
        self.closing_tag = "</span>"

    @staticmethod
    def format_placeholders(value):
        if not value:
            return value
        return re.sub(
            r"\(\(([^\)]+)\)\)",  # anything that looks like ((registration number))
            lambda match: "<span class='placeholder'>{}</span>".format(match.group(1)),
            value
        )

    @staticmethod
    def replace_placeholders(template, values):
        if not template:
            return template
        return re.sub(
            r"\(\(([^\)]+)\)\)",  # anything that looks like ((registration number))
            lambda match: values.get(match.group(1), ''),
            template
        )
