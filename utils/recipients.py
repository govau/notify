import re
import csv
from flask import Markup

from utils.template import Template


first_column_heading = {
    'email': 'email address',
    'sms': 'phone number'
}

email_regex = re.compile(r"(^[^\@^\s]+@[^\@^\s]+(\.[^\@^\.^\s]+)$)")


class RecipientCSV():

    reader_options = {
        'quoting': csv.QUOTE_NONE,
        'skipinitialspace': True
    }

    def __init__(
        self,
        file_data,
        template_type=None,
        placeholders=None
    ):
        self.file_data = file_data
        self.template_type = template_type
        self.placeholders = placeholders or []

    @property
    def rows(self):
        for row in csv.DictReader(
            self.file_data.strip().splitlines(),
            **RecipientCSV.reader_options
        ):
            yield row

    @property
    def recipients(self):
        for row in self.rows:
            yield self._get_recipient_from_row(row)

    @property
    def personalisation(self):
        for row in self.rows:
            yield self._get_personalisation_from_row(row)

    @property
    def recipients_and_personalisation(self):
        for row in self.rows:
            yield (
                self._get_recipient_from_row(row),
                self._get_personalisation_from_row(row)
            )

    @property
    def column_headers(self):
        for row in csv.reader(
            self.file_data.strip().splitlines(),
            **RecipientCSV.reader_options
        ):
            return row
        return []

    @property
    def column_headers_with_placeholders_highlighted(self):
        return [
            Markup(Template.placeholder_tag.format(header)) if header in self.placeholders else header
            for header in self.column_headers
        ]

    def _get_recipient_from_row(self, row):
        return row[
            first_column_heading[self.template_type]
        ]

    def _get_personalisation_from_row(self, row):
        copy_of_row = row.copy()
        copy_of_row.pop(first_column_heading[self.template_type], None)
        return copy_of_row


class InvalidEmailError(Exception):
    def __init__(self, message):
        self.message = message


class InvalidPhoneError(InvalidEmailError):
    pass


def validate_phone_number(number):

    for character in ['(', ')', ' ', '-']:
        number = number.replace(character, '')

    number = number.lstrip('+')

    try:
        list(map(int, number))
    except ValueError:
        raise InvalidPhoneError('Must not contain letters or symbols')

    if not any(
        number.startswith(prefix)
        for prefix in ['07', '447', '4407', '00447']
    ):
        raise InvalidPhoneError('Not a UK mobile number')

    # Split number on first 7
    number = number.split('7', 1)[1]

    if len(number) > 9:
        raise InvalidPhoneError('Too many digits')

    if len(number) < 9:
        raise InvalidPhoneError('Not enough digits')

    return number


def format_phone_number(number):
    return '+447{}'.format(number)


def validate_email_address(email_address):
    if not re.match(email_regex, email_address):
        raise InvalidEmailError('Not a valid email address')


def validate_recipient(recipient, template_type):
    return {
        'email': validate_email_address,
        'sms': validate_phone_number
    }[template_type](recipient)
