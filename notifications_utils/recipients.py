import re
import sys
import csv
from contextlib import suppress
from functools import lru_cache, partial
from collections import OrderedDict
from orderedset import OrderedSet

from flask import Markup

from notifications_utils.template import Template
from notifications_utils.columns import Columns
from notifications_utils.international_billing_rates import COUNTRY_PREFIXES


uk_prefix = '44'

first_column_headings = {
    'email': ['email address'],
    'sms': ['phone number'],
    'letter': [
        'address line 1',
        'address line 2',
        'address line 3',
        'address line 4',
        'address line 5',
        'address line 6',
        'postcode',
    ],
}

optional_address_columns = {
    'address line 3',
    'address line 4',
    'address line 5',
    'address line 6',
}

# regexes for use in validate_email_address
email_regex = re.compile(r'^[^\s";@]+@([^.@][^@]+)$')
hostname_part = re.compile(r'^(xn-|[a-z0-9]+)(-[a-z0-9]+)*$', re.IGNORECASE)
tld_part = re.compile(r'^([a-z]{2,63}|xn--([a-z0-9]+-)*[a-z0-9]+)$', re.IGNORECASE)


class RecipientCSV():

    missing_field_error = 'Missing'

    max_rows = 50000

    def __init__(
        self,
        file_data,
        template_type=None,
        placeholders=None,
        max_errors_shown=20,
        max_initial_rows_shown=10,
        whitelist=None,
        template=None,
        remaining_messages=sys.maxsize,
        sms_character_limit=0
    ):
        self.file_data = file_data.strip(', \n\r\t')
        self.template_type = template_type
        self.character_limit = int(sms_character_limit) if self.template_type == 'sms' else sys.maxsize
        self.placeholders = placeholders
        self.max_errors_shown = max_errors_shown
        self.max_initial_rows_shown = max_initial_rows_shown
        self.whitelist = whitelist
        self.template = template if isinstance(template, Template) else None
        self.annotated_rows = list(self.get_annotated_rows())
        self.remaining_messages = remaining_messages

    def __len__(self):
        if not hasattr(self, '_len'):
            self._len = len(list(self.rows))
        return self._len

    @property
    def whitelist(self):
        return self._whitelist

    @whitelist.setter
    def whitelist(self, value):
        try:
            self._whitelist = list(value)
        except TypeError:
            self._whitelist = []

    @property
    def placeholders(self):
        return self._placeholders

    @placeholders.setter
    def placeholders(self, value):
        try:
            self._placeholders = list(value) + self.recipient_column_headers
        except TypeError:
            self._placeholders = self.recipient_column_headers
        self.placeholders_as_column_keys = [
            Columns.make_key(placeholder)
            for placeholder in self._placeholders
        ]
        self.recipient_column_headers_as_column_keys = [
            Columns.make_key(placeholder)
            for placeholder in self.recipient_column_headers
        ]

    @property
    def template_type(self):
        return self._template_type

    @template_type.setter
    def template_type(self, value):
        self._template_type = value
        self.recipient_column_headers = first_column_headings[self.template_type]

    @property
    def has_errors(self):
        return bool(
            self.missing_column_headers or
            self.more_rows_than_can_send or
            self.too_many_rows or
            (not self.allowed_to_send_to) or
            self.rows_with_missing_data or
            self.rows_with_bad_recipients or
            self.rows_with_message_too_long
        )  # This is 3x faster than using `any()`

    @property
    def allowed_to_send_to(self):
        if self.template_type == 'letter':
            return True
        if not self.whitelist:
            return True
        return all(
            allowed_to_send_to(recipient, self.whitelist)
            for recipient in self.recipients
        )

    @property
    def _rows(self):
        return csv.reader(
            self.file_data.strip().splitlines(),
            quoting=csv.QUOTE_MINIMAL,
            skipinitialspace=True,
        )

    @property
    def rows(self):

        column_headers = self._raw_column_headers  # this is for caching
        length_of_column_headers = len(column_headers)

        rows_as_lists_of_columns = self._rows

        next(rows_as_lists_of_columns)  # skip the header row

        for row in rows_as_lists_of_columns:

            output_dict = OrderedDict()

            for column_name, column_value in zip(column_headers, row):
                insert_or_append_to_dict(output_dict, column_name, column_value or None)

            length_of_row = len(row)

            if length_of_column_headers < length_of_row:
                output_dict[None] = row[length_of_column_headers:]
            elif length_of_column_headers > length_of_row:
                for key in column_headers[length_of_row:]:
                    insert_or_append_to_dict(output_dict, key, None)

            yield Columns(output_dict)

    @property
    def rows_with_errors(self):
        return self.rows_with_missing_data | self.rows_with_bad_recipients | self.rows_with_message_too_long

    @property
    def rows_with_missing_data(self):
        return set(
            row['index'] for row in self.annotated_rows if any(
                value.get('error') == self.missing_field_error
                for key, value in row['columns'].items()
            )
        )

    @property
    def rows_with_bad_recipients(self):
        return set(
            row['index'] for row in self.annotated_rows if any(
                row['columns'].get(recipient_column, {}).get('error')
                not in [None, self.missing_field_error]
                for recipient_column in self.recipient_column_headers
            )
        )

    @property
    def rows_with_message_too_long(self):
        return set(
            row['index'] for row in self.annotated_rows if row['message_too_long']
        )

    @property
    def more_rows_than_can_send(self):
        return len(self) > self.remaining_messages

    @property
    def too_many_rows(self):
        return len(self) > self.max_rows

    def get_annotated_rows(self):
        if self.too_many_rows:
            return []
        for row_index, row in enumerate(self.rows):
            if self.template:
                self.template.values = dict(row.items())
            yield dict(
                columns=Columns({key: {
                    'data': value,
                    'error': self._get_error_for_field(key, value),
                    'ignore': (
                        key not in self.placeholders_as_column_keys
                    )
                } for key, value in row.items()}),
                index=row_index,
                message_too_long=bool(
                    self.template and
                    self.template.content_count > self.character_limit
                )
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
    def enumerated_recipients_and_personalisation(self):
        for row_index, row in enumerate(self.rows):
            yield (
                row_index,
                self._get_recipient_from_row(row),
                self._get_personalisation_from_row(row)
            )

    @property
    def recipients_and_personalisation(self):
        for row in self.rows:
            yield (
                self._get_recipient_from_row(row),
                self._get_personalisation_from_row(row)
            )

    @property
    def _raw_column_headers(self):
        for row in self._rows:
            return row
        return []

    @property
    def column_headers(self):
        return list(OrderedSet(self._raw_column_headers))

    @property
    def column_headers_as_column_keys(self):
        return Columns.from_keys(self.column_headers).keys()

    @property
    def missing_column_headers(self):
        return set(
            key for key in self.placeholders
            if (
                Columns.make_key(key) not in self.column_headers_as_column_keys and
                not self.is_optional_address_column(key)
            )
        )

    def is_optional_address_column(self, key):
        return (
            self.template_type == 'letter' and
            Columns.make_key(key) in Columns.from_keys(optional_address_columns).keys()
        )

    @property
    def has_recipient_columns(self):
        return set(
            Columns.make_key(recipient_column)
            for recipient_column in self.recipient_column_headers
            if not self.is_optional_address_column(recipient_column)
        ) <= self.column_headers_as_column_keys

    def _get_error_for_field(self, key, value):

        if self.is_optional_address_column(key):
            return

        if key in self.recipient_column_headers_as_column_keys:
            if value in [None, '']:
                return self.missing_field_error
            try:
                validate_recipient(value, self.template_type, column=key)
            except (InvalidEmailError, InvalidPhoneError, InvalidAddressError) as error:
                return str(error)

        if key not in self.placeholders_as_column_keys:
            return

        if value in [None, '']:
            return self.missing_field_error

    def _get_recipient_from_row(self, row):
        if len(self.recipient_column_headers) == 1:
            return row[
                self.recipient_column_headers[0]
            ]
        else:
            return [
                row[column] for column in self.recipient_column_headers
            ]

    def _get_personalisation_from_row(self, row):
        return Columns({
            key: value for key, value in row.items() if key in self.placeholders_as_column_keys
        })

    @staticmethod
    def row_has_error(row):
        return any(
            key != 'index' and value.get('error') for key, value in row['columns'].items()
        )


class InvalidEmailError(Exception):

    def __init__(self, message=None):
        super().__init__(message or 'Not a valid email address')


class InvalidPhoneError(InvalidEmailError):
    pass


class InvalidAddressError(InvalidEmailError):
    pass


def normalise_phone_number(number):

    for character in ['(', ')', ' ', '-', '+']:
        number = number.replace(character, '')

    try:
        list(map(int, number))
    except ValueError:
        raise InvalidPhoneError('Must not contain letters or symbols')

    return number.lstrip('0')


def validate_uk_phone_number(number, column=None):

    number = normalise_phone_number(number).lstrip('44').lstrip('0')

    if not number.startswith('7'):
        raise InvalidPhoneError('Not a UK mobile number')

    if len(number) > 10:
        raise InvalidPhoneError('Too many digits')

    if len(number) < 10:
        raise InvalidPhoneError('Not enough digits')

    return number


def validate_phone_number(number, column=None, international=False):

    if (
        (not international) or
        (number.startswith('0') and not number.startswith('00'))
    ):
        return validate_uk_phone_number(number)

    number = normalise_phone_number(number)

    if (
        number.startswith('44') or
        (number.startswith('7') and len(number) < 11)
    ):
        return validate_uk_phone_number(number)

    if len(number) < 5:
        raise InvalidPhoneError('Not enough digits')

    if not any(
        number.startswith(prefix) for prefix in COUNTRY_PREFIXES
    ):
        raise InvalidPhoneError('Not a valid country prefix')

    return number


def format_phone_number(number):
    return '+44{}'.format(number)


def format_phone_number_human_readable(number):
    return '0{} {} {}'.format(number[:4], number[4:7], number[7:10])


def validate_and_format_phone_number(number, human_readable=False):
    if human_readable:
        return format_phone_number_human_readable(validate_phone_number(number))
    return format_phone_number(validate_phone_number(number))


def validate_email_address(email_address, column=None):
    # almost exactly the same as by https://github.com/wtforms/wtforms/blob/master/wtforms/validators.py,
    # with minor tweaks for SES compatibility - to avoid complications we are a lot stricter with the local part
    # than neccessary - we don't allow any double quotes or semicolons to prevent SES Technical Failures
    email_address = email_address.strip()
    match = re.match(email_regex, email_address)

    # not an email
    if not match:
        raise InvalidEmailError

    hostname = match.group(1)
    # don't allow consecutive periods in domain names
    if '..' in hostname:
        raise InvalidEmailError

    # idna = "Internationalized domain name" - this encode/decode cycle converts unicode into its accurate ascii
    # representation as the web uses. '例え.テスト'.encode('idna') == b'xn--r8jz45g.xn--zckzah'
    hostname = hostname.encode('idna').decode('ascii')
    parts = hostname.split('.')

    if len(hostname) > 253 or len(parts) < 2:
        raise InvalidEmailError

    for part in parts:
        if not part or len(part) > 63 or not hostname_part.match(part):
            raise InvalidEmailError

    # if the part after the last . is not a valid TLD then bail out
    if not tld_part.match(parts[-1]):
        raise InvalidEmailError

    return email_address


def format_email_address(email_address):
    return email_address.lower()


def validate_and_format_email_address(email_address):
    return format_email_address(validate_email_address(email_address))


def validate_address(address_line, column):
    if Columns.make_key(column) in Columns.from_keys(optional_address_columns).keys():
        return address_line
    if Columns.make_key(column) not in Columns.from_keys(first_column_headings['letter']).keys():
        raise TypeError
    if not address_line or not address_line.strip():
        raise InvalidAddressError('Missing')
    return address_line


def validate_recipient(recipient, template_type, column=None, international_sms=False):
    return {
        'email': validate_email_address,
        'sms': partial(validate_phone_number, international=international_sms),
        'letter': validate_address,
    }[template_type](recipient, column)


@lru_cache(maxsize=32, typed=False)
def format_recipient(recipient):
    with suppress(InvalidPhoneError):
        return validate_and_format_phone_number(recipient)
    with suppress(InvalidEmailError):
        return validate_and_format_email_address(recipient)
    return recipient


def allowed_to_send_to(recipient, whitelist):
    return format_recipient(recipient) in [
        format_recipient(recipient) for recipient in whitelist
    ]


def insert_or_append_to_dict(dict_, key, value):
    if dict_.get(key):
        if isinstance(dict_[key], list):
            dict_[key].append(value)
        else:
            dict_[key] = [dict_[key], value]
    else:
        dict_.update({key: value})
