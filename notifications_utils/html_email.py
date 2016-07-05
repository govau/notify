import re
import urllib
from os import path
from jinja2 import Environment, FileSystemLoader


email_template = Environment(loader=FileSystemLoader(
    path.dirname(path.abspath(__file__))
)).get_template('email_template.jinja2')


govuk_not_a_link = re.compile(
    r'(?<!\.|\/)(GOV)\.(UK)(?!\/|\?)',
    re.IGNORECASE
)


class HTMLEmail():

    def __init__(self, govuk_banner=True, complete_html=True):
        self.govuk_banner = govuk_banner
        self.complete_html = complete_html

    def __call__(self, body):
        return email_template.render({
            'body': self.linkify(self.unlink_govuk_escaped(body)),
            'govuk_banner': self.govuk_banner,
            'complete_html': self.complete_html
        })

    @staticmethod
    def unlink_govuk_escaped(message):
        return re.sub(
            govuk_not_a_link,
            r'\1' + '.\u200B' + r'\2',  # Unicode zero-width space
            message
        )

    @staticmethod
    def linkify(text):
        return re.sub(
            r'(https?://\S+)',
            lambda match: '<a href="{}">{}</a>'.format(
                urllib.parse.quote(
                    urllib.parse.unquote(match.group(1)),
                    safe=':/?#=&'
                ),
                match.group(1)
            ),
            text
        )
