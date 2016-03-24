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
        placeholders=None,
        max_errors_shown=20,
        max_initial_rows_shown=10
    ):
        self.file_data = file_data.strip(', \n\r\t')
        self.template_type = template_type
        self.placeholders = placeholders or []
        self.max_errors_shown = max_errors_shown
        self.max_initial_rows_shown = max_initial_rows_shown

    @property
    def recipient_column_header(self):
        return first_column_heading[self.template_type]

    @property
    def has_errors(self):
        return any((
            self.missing_column_headers,
            any(self.rows_with_errors)
        ))

    @property
    def rows(self):
        for row in csv.DictReader(
            self.file_data.strip().splitlines(),
            **RecipientCSV.reader_options
        ):
            yield row

    @property
    def rows_with_errors(self):
        return self.rows_with_missing_data | self.rows_with_bad_recipients

    @property
    def rows_with_missing_data(self):
        return set(
            row['index'] for row in self.annotated_rows if any(
                key not in [self.recipient_column_header, 'index'] and value.get('error')
                for key, value in row.items()
            )
        )

    @property
    def rows_with_bad_recipients(self):
        return set(
            row['index'] for row in self.annotated_rows if row.get(self.recipient_column_header, {}).get('error')
        )

    @property
    def annotated_rows(self):
        for row_index, row in enumerate(self.rows):
            yield dict(
                {key: {
                    'data': value,
                    'error': self._get_error_for_field(key, value),
                    'ignore': (key != self.recipient_column_header and key not in self.placeholders)
                } for key, value in row.items()},
                index=row_index
            )

    @property
    def initial_annotated_rows(self):
        for row in self.annotated_rows:
            if row['index'] < self.max_initial_rows_shown:
                yield row

    @property
    def annotated_rows_with_errors(self):
        for row in self.annotated_rows:
            if RecipientCSV.row_has_error(row):
                yield row

    @property
    def initial_annotated_rows_with_errors(self):
        for row_index, row in enumerate(self.annotated_rows_with_errors):
            if row_index < self.max_errors_shown:
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
    def missing_column_headers(self):
        return set([self.recipient_column_header] + list(self.placeholders)) - set(self.column_headers)

    @property
    def column_headers_with_placeholders_highlighted(self):
        return [
            Markup(Template.placeholder_tag.format(header)) if header in self.placeholders else header
            for header in self.column_headers
        ]

    def _get_error_for_field(self, key, value):
        if key == self.recipient_column_header:
            try:
                validate_recipient(value, self.template_type)
            except (InvalidEmailError, InvalidPhoneError) as error:
                return str(error)
        if key not in self.placeholders:
            return None
        if value in [None, '']:
            return 'Missing'

    def _get_recipient_from_row(self, row):
        return row[
            self.recipient_column_header
        ]

    def _get_personalisation_from_row(self, row):
        return {
            key: value for key, value in row.items() if key in self.placeholders
        }

    @staticmethod
    def row_has_error(row):
        return any(
            key != 'index' and value.get('error') for key, value in row.items()
        )


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
