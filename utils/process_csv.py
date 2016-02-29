import csv


first_column_heading = {
    'email': 'email address',
    'sms': 'phone number'
}


def get_rows_from_csv(file_data):
    for row in csv.DictReader(
        file_data.strip().splitlines(),
        lineterminator='\n',
        quoting=csv.QUOTE_NONE,
        skipinitialspace=True
    ):
        yield row


def get_recipient_from_row(row, template_type):
    return row[
        first_column_heading[template_type]
    ].replace(' ', '')
