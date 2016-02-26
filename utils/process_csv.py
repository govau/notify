import csv


first_column_heading = {
    'email': 'email address',
    'sms': 'phone number'
}


def get_recipients_from_csv(file_data, template_type):
    for row in csv.DictReader(
        file_data.strip().splitlines(),
        lineterminator='\n',
        quoting=csv.QUOTE_NONE,
        skipinitialspace=True
    ):
        yield row[
            first_column_heading[template_type]
        ].replace(' ', '')
