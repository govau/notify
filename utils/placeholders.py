import re


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
            self.pattern,
            lambda match: "{}{}{}".format(self.opening_tag, match.group(1), self.closing_tag),
            self.template
        )

    def replace(self, values):

        return re.sub(
            self.pattern,
            lambda match: values.get(match.group(1), ''),
            self.template
        )
