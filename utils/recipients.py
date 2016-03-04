import csv


first_column_heading = {
    'email': 'email address',
    'sms': 'phone number'
}


class RecipientCSV():

    def __init__(
        self,
        file_data,
        template_type=None
    ):
        self.file_data = file_data
        self.template_type = template_type

    @property
    def rows(self):
        for row in csv.DictReader(
            self.file_data.strip().splitlines(),
            lineterminator='\n',
            quoting=csv.QUOTE_NONE,
            skipinitialspace=True
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

    def _get_recipient_from_row(self, row):
        return row[
            first_column_heading[self.template_type]
        ]

    def _get_personalisation_from_row(self, row):
        copy_of_row = row.copy()
        copy_of_row.pop(first_column_heading[self.template_type], None)
        return copy_of_row
