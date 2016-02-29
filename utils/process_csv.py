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


def get_recipients_from_csv(file_data, template_type):
    for row in get_rows_from_csv(file_data):
        yield row[
            first_column_heading[template_type]
        ].replace(' ', '')
