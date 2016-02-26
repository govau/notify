import csv


def get_recipients_from_csv(file_data):
    for row in csv.DictReader(
        file_data.splitlines(),
        lineterminator='\n',
        quoting=csv.QUOTE_NONE
    ):
        yield row['to'].replace(' ', '')
