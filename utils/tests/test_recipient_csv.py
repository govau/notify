import pytest
import itertools
from functools import partial
from orderedset import OrderedSet

from notifications_utils.recipients import RecipientCSV
from notifications_utils.template import SMSMessageTemplate


def _index_rows(rows):
    return set(row.index for row in rows)


@pytest.mark.parametrize(
    "file_contents,template_type,expected",
    [
        (
            "",
            "sms",
            [],
        ),
        (
            "phone number",
            "sms",
            [],
        ),
        (
            """
                phone number,name
                +44 123, test1
                +44 456,test2
            """,
            "sms",
            [
                [('phone number', '+44 123'), ('name', 'test1')],
                [('phone number', '+44 456'), ('name', 'test2')]
            ]
        ),
        (
            """
                phone number,name
                +44 123,
                +44 456
            """,
            "sms",
            [
                [('phone number', '+44 123'), ('name', None)],
                [('phone number', '+44 456'), ('name', None)]
            ]
        ),
        (
            """
                email address,name
                test@example.com,test1
                test2@example.com, test2
            """,
            "email",
            [
                [('email address', 'test@example.com'), ('name', 'test1')],
                [('email address', 'test2@example.com'), ('name', 'test2')]
            ]
        ),
        (
            """
                email address
                test@example.com,test1,red
                test2@example.com, test2,blue
            """,
            "email",
            [
                [('email address', 'test@example.com'), (None, ['test1', 'red'])],
                [('email address', 'test2@example.com'), (None, ['test2', 'blue'])]
            ]
        ),
        (
            """
                email address,name
                test@example.com,"test1"
                test2@example.com," test2"
            """,
            "email",
            [
                [('email address', 'test@example.com'), ('name', 'test1')],
                [('email address', 'test2@example.com'), ('name', ' test2')]
            ]
        ),
        (
            """
                email address,date,name
                test@example.com,"Nov 28, 2016",test1
                test2@example.com,"Nov 29, 2016",test2
            """,
            "email",
            [
                [('email address', 'test@example.com'), ('date', 'Nov 28, 2016'), ('name', 'test1')],
                [('email address', 'test2@example.com'), ('date', 'Nov 29, 2016'), ('name', 'test2')]
            ]
        ),
        (
            """
                address_line_1
                Alice
                Bob
            """,
            "letter",
            [
                [('address_line_1', 'Alice')],
                [('address_line_1', 'Bob')]
            ]
        ),
        (
            """
                address line 1,address line 2,address line 5,address line 6,postcode,name,thing
                A. Name,,,,XM4 5HQ,example,example
            """,
            "letter",
            [[
                ('addressline1', 'A. Name'),
                ('addressline2', None),
                # optional address rows 3 and 4 not in file
                ('addressline5', None),
                ('addressline5', None),
                ('postcode', 'XM4 5HQ'),
                ('name', 'example'),
                ('thing', 'example'),
            ]]
        ),
        (
            """
                phone number, list, list, list
                07900900001, cat, rat, gnat
                07900900002, dog, hog, frog
                07900900003, elephant
            """,
            "sms",
            [
                [
                    ('phone number', '07900900001'),
                    ('list', ['cat', 'rat', 'gnat'])
                ],
                [
                    ('phone number', '07900900002'),
                    ('list', ['dog', 'hog', 'frog'])
                ],
                [
                    ('phone number', '07900900003'),
                    ('list', ['elephant', None, None])
                ],
            ]
        )
    ]
)
def test_get_rows(file_contents, template_type, expected):
    rows = list(RecipientCSV(file_contents, template_type=template_type).rows)
    if not expected:
        assert rows == expected
    for index, row in enumerate(expected):
        assert len(rows[index].items()) == len(row)
        for key, value in row:
            assert rows[index].get(key).data == value


@pytest.mark.parametrize(
    "file_contents,template_type,expected",
    [
        (
            """
                phone number,name
                07700900460, test1
                +447700 900 460,test2
                ,
            """,
            'sms',
            [
                {
                    'index': 0,
                    'message_too_long': False
                },
                {
                    'index': 1,
                    'message_too_long': False
                },
            ]
        ),
        (
            """
                email address,name,colour
                test@example.com,test1,blue
                test2@example.com, test2,red
            """,
            'email',
            [
                {
                    'index': 0,
                    'message_too_long': False
                },
                {
                    'index': 1,
                    'message_too_long': False
                },
            ]
        )
    ]
)
def test_get_annotated_rows(file_contents, template_type, expected):
    recipients = RecipientCSV(
        file_contents,
        template_type=template_type,
        placeholders=['name'],
        max_initial_rows_shown=1
    )
    for index, expected_row in enumerate(expected):
        annotated_row = list(recipients.rows)[index]
        assert annotated_row.index == expected_row['index']
        assert annotated_row.message_too_long == expected_row['message_too_long']
    assert len(list(recipients.rows)) == 2
    assert len(list(recipients.initial_rows)) == 1
    assert not recipients.has_errors


def test_get_rows_with_errors():
    recipients = RecipientCSV(
        """
            email address, name
            a@b.com,
            a@b.com,
            a@b.com,
            a@b.com,
            a@b.com,
            a@b.com,


        """,
        template_type='email',
        placeholders=['name'],
        max_errors_shown=3
    )
    assert len(list(recipients.rows_with_errors)) == 6
    assert len(list(recipients.initial_rows_with_errors)) == 3
    assert recipients.has_errors


@pytest.mark.parametrize('template_type, row_count, header, filler, row_with_error', [
    ('email', 500, "email address\n", "test@example.com\n", "test at example dot com"),
    ('sms', 500, "phone number\n", "07900900123\n", "12345"),
])
def test_big_list_validates_right_through(template_type, row_count, header, filler, row_with_error):
    big_csv = RecipientCSV(
        header + (filler * (row_count - 1) + row_with_error),
        template_type=template_type,
        max_errors_shown=100,
        max_initial_rows_shown=3
    )
    assert len(list(big_csv.rows)) == row_count
    assert _index_rows(big_csv.rows_with_bad_recipients) == {row_count - 1}  # 0 indexed
    assert _index_rows(big_csv.rows_with_errors) == {row_count - 1}
    assert len(list(big_csv.initial_rows_with_errors)) == 1
    assert big_csv.has_errors


def test_big_list():
    big_csv = RecipientCSV(
        "email address,name\n" + ("a@b.com\n" * RecipientCSV.max_rows),
        template_type='email',
        placeholders=['name'],
        max_errors_shown=100,
        max_initial_rows_shown=3,
        whitelist=["a@b.com"]
    )
    assert len(list(big_csv.initial_rows)) == 3
    assert len(list(big_csv.initial_rows_with_errors)) == 100
    assert len(list(big_csv.rows)) == RecipientCSV.max_rows
    assert big_csv.has_errors


@pytest.mark.parametrize(
    "file_contents,template_type,placeholders,expected_recipients,expected_personalisation",
    [
        (
            """
                phone number,name, date
                +44 123,test1,today
                +44456,    ,tomorrow
                ,,
                , ,
            """,
            'sms',
            ['name'],
            ['+44 123', '+44456'],
            [{'name': 'test1'}, {'name': None}]
        ),
        (
            """
                email address,name,colour
                test@example.com,test1,red
                testatexampledotcom,test2,blue
            """,
            'email',
            ['colour'],
            ['test@example.com', 'testatexampledotcom'],
            [
                {'colour': 'red'},
                {'colour': 'blue'}
            ]
        ),
        (
            """
                email address
                test@example.com,test1,red
                testatexampledotcom,test2,blue
            """,
            'email',
            [],
            ['test@example.com', 'testatexampledotcom'],
            []
        )
    ]
)
def test_get_recipient(file_contents, template_type, placeholders, expected_recipients, expected_personalisation):

    recipients = RecipientCSV(file_contents, template_type=template_type, placeholders=placeholders)

    for index, row in enumerate(expected_personalisation):
        for key, value in row.items():
            assert recipients[index].recipient == expected_recipients[index]
            assert recipients[index].personalisation.get(key) == value


@pytest.mark.parametrize(
    "file_contents,template_type,placeholders,expected_recipients,expected_personalisation",
    [
        (
            """
                email address,test
                test@example.com,test1,red
                testatexampledotcom,test2,blue
            """,
            'email',
            ['test'],
            [
                (0, 'test@example.com'),
                (1, 'testatexampledotcom')
            ],
            [
                {'emailaddress': 'test@example.com', 'test': 'test1'},
                {'emailaddress': 'testatexampledotcom', 'test': 'test2'},
            ],
        )
    ]
)
def test_get_recipient_respects_order(file_contents,
                                      template_type,
                                      placeholders,
                                      expected_recipients,
                                      expected_personalisation):
    recipients = RecipientCSV(file_contents, template_type=template_type, placeholders=placeholders)

    for row, email in expected_recipients:
        assert (
            recipients[row].index,
            recipients[row].recipient,
            recipients[row].personalisation,
        ) == (
            row,
            email,
            expected_personalisation[row],
        )


@pytest.mark.parametrize(
    "file_contents,template_type,expected,expected_missing",
    [
        (
            "", 'sms', [], set(['phone number', 'name'])
        ),
        (
            """
                phone number,name
                07700900460,test1
                07700900460,test1
                07700900460,test1
            """,
            'sms',
            ['phone number', 'name'],
            set()
        ),
        (
            """
                email address,name,colour
            """,
            'email',
            ['email address', 'name', 'colour'],
            set()
        ),
        (
            """
                address_line_1, address_line_2, postcode, name
            """,
            'letter',
            ['address_line_1', 'address_line_2', 'postcode', 'name'],
            set()
        ),
        (
            """
                email address,colour
            """,
            'email',
            ['email address', 'colour'],
            set(['name'])
        ),
        (
            """
                address_line_1, address_line_2, name
            """,
            'letter',
            ['address_line_1', 'address_line_2', 'name'],
            set(['postcode'])
        ),
        (
            """
                phone number,list,list,name,list
            """,
            'sms',
            ['phone number', 'list', 'name'],
            set()
        ),
    ]
)
def test_column_headers(file_contents, template_type, expected, expected_missing):
    recipients = RecipientCSV(file_contents, template_type=template_type, placeholders=['name'])
    assert recipients.column_headers == expected
    assert recipients.missing_column_headers == expected_missing
    assert recipients.has_errors == bool(expected_missing)


@pytest.mark.parametrize(
    'placeholders',
    [
        None,
        ['name']
    ]
)
@pytest.mark.parametrize(
    'file_contents,template_type',
    [
        pytest.mark.xfail(('', 'sms')),
        pytest.mark.xfail(('name', 'sms')),
        pytest.mark.xfail(('email address', 'sms')),
        pytest.mark.xfail((
            # missing postcode
            'address_line_1, address_line_2, address_line_3, address_line_4, address_line_5',
            'letter'
        )),
        ('phone number', 'sms'),
        ('phone number,name', 'sms'),
        ('email address', 'email'),
        ('email address,name', 'email'),
        ('PHONENUMBER', 'sms'),
        ('email_address', 'email'),
        (
            'address_line_1, address_line_2, postcode',
            'letter'
        ),
        (
            'address_line_1, address_line_2, address_line_3, address_line_4, address_line_5, address_line_6, postcode',
            'letter'
        ),
    ]
)
def test_recipient_column(placeholders, file_contents, template_type):
    assert RecipientCSV(file_contents, template_type=template_type, placeholders=placeholders).has_recipient_columns


@pytest.mark.parametrize(
    "file_contents,template_type,rows_with_bad_recipients,rows_with_missing_data",
    [
        (
            """
                phone number,name,date
                07700900460,test1,test1
                07700900460,test1
                +44 123,test1,test1
                07700900460,test1,test1
                07700900460,test1
                +1644000000,test1,test1
                ,test1,test1
            """,
            'sms',
            {2, 5}, {1, 4, 6}
        ),
        (
            """
                phone number,name
                07700900460,test1,test2
            """,
            'sms',
            set(), set()
        ),
        (
            """
            """,
            'sms',
            set(), set()
        ),
        (
            # missing postcode
            """
                address_line_1,address_line_2,address_line_3,address_line_4,address_line_5,postcode,date
                name,          building,      street,        town,          county,        postcode,today
                name,          building,      street,        town,          county,        ,        today
            """,
            'letter',
            set(), {1}
        ),
        (
            # only required address fields
            """
                address_line_1, postcode, date
                name,           postcode, today
            """,
            'letter',
            set(), set()
        ),
        (
            # optional address fields not filled in
            """
                address_line_1,address_line_2,address_line_3,address_line_4,address_line_5,postcode,date
                name          ,123 fake st.  ,              ,              ,              ,postcode,today
            """,
            'letter',
            set(), set()
        ),
    ]
)
@pytest.mark.parametrize('partial_instance', [
    partial(RecipientCSV),
    partial(RecipientCSV, international_sms=False),
])
def test_bad_or_missing_data(
    file_contents, template_type, rows_with_bad_recipients, rows_with_missing_data, partial_instance
):
    recipients = partial_instance(file_contents, template_type=template_type, placeholders=['date'])
    assert _index_rows(recipients.rows_with_bad_recipients) == rows_with_bad_recipients
    assert _index_rows(recipients.rows_with_missing_data) == rows_with_missing_data
    if rows_with_bad_recipients or rows_with_missing_data:
        assert recipients.has_errors is True


@pytest.mark.parametrize("file_contents,rows_with_bad_recipients", [
    (
        """
            phone number
            800000000000
            1234
            +447900123
        """,
        {0, 1, 2},
    ),
    (
        """
            phone number, country
            1-202-555-0104, USA
            +12025550104, USA
            23051234567, Mauritius
        """,
        set(),
    ),
])
def test_international_recipients(file_contents, rows_with_bad_recipients):
    recipients = RecipientCSV(file_contents, template_type='sms', international_sms=True)
    assert _index_rows(recipients.rows_with_bad_recipients) == rows_with_bad_recipients


def test_errors_when_too_many_rows():
    recipients = RecipientCSV(
        "email address\n" + ("a@b.com\n" * (RecipientCSV.max_rows + 1)),
        template_type='email'
    )
    assert RecipientCSV.max_rows == 50000
    assert recipients.too_many_rows is True
    assert recipients.has_errors is True
    assert recipients.rows[49000]['email_address'].data == 'a@b.com'
    # We stop processing subsequent rows
    assert recipients.rows[50000] is None


@pytest.mark.parametrize(
    "file_contents,template_type,whitelist,count_of_rows_with_errors",
    [
        (
            """
                phone number
                07700900460
                07700900461
                07700900462
                07700900463
            """,
            'sms',
            ['+447700900460'],  # Same as first phone number but in different format
            3
        ),
        (
            """
                phone number
                7700900460
                447700900461
                07700900462
            """,
            'sms',
            ['07700900460', '07700900461', '07700900462', '07700900463', 'test@example.com'],
            0
        ),
        (
            """
                email address
                IN_WHITELIST@EXAMPLE.COM
                not_in_whitelist@example.com
            """,
            'email',
            ['in_whitelist@example.com', '07700900460'],  # Email case differs to the one in the CSV
            1
        )
    ]
)
def test_recipient_whitelist(file_contents, template_type, whitelist, count_of_rows_with_errors):

    recipients = RecipientCSV(
        file_contents,
        template_type=template_type,
        whitelist=whitelist
    )

    if count_of_rows_with_errors:
        assert not recipients.allowed_to_send_to
    else:
        assert recipients.allowed_to_send_to

    # Make sure the whitelist isn’t emptied by reading it. If it’s an iterator then
    # there’s a risk that it gets emptied after being read once
    recipients.whitelist = (str(fake_number) for fake_number in range(7700900888, 7700900898))
    list(recipients.whitelist)
    assert not recipients.allowed_to_send_to
    assert recipients.has_errors

    # An empty whitelist is treated as no whitelist at all
    recipients.whitelist = []
    assert recipients.allowed_to_send_to
    recipients.whitelist = itertools.chain()
    assert recipients.allowed_to_send_to


def test_detects_rows_which_result_in_overly_long_messages():
    template = SMSMessageTemplate(
        {'content': '((placeholder))', 'template_type': 'sms'},
        sender=None,
        prefix=None,
    )
    recipients = RecipientCSV(
        """
            phone number,placeholder
            07700900460,1
            07700900461,{one_under}
            07700900462,{exactly}
            07700900463,{one_over}
        """.format(
            one_under='a' * 458,
            exactly='a' * 459,
            one_over='a' * 460,
        ),
        template_type=template.template_type,
        template=template
    )
    assert _index_rows(recipients.rows_with_errors) == {3}
    assert _index_rows(recipients.rows_with_message_too_long) == {3}
    assert recipients.has_errors


@pytest.mark.parametrize(
    "key, expected",
    sum([
        [(key, expected) for key in group] for expected, group in [
            ('07700900460', (
                'phone number',
                '   PHONENUMBER',
                'phone_number',
                'phone-number',
                'phoneNumber'
            )),
            ('Jo', (
                'FIRSTNAME',
                'first name',
                'first_name ',
                'first-name',
                'firstName'
            )),
            ('Bloggs', (
                'Last    Name',
                'LASTNAME',
                '    last_name',
                'last-name',
                'lastName   '
            ))
        ]
    ], [])
)
def test_ignores_spaces_and_case_in_placeholders(key, expected):
    recipients = RecipientCSV(
        """
            phone number,FIRSTNAME, Last Name
            07700900460, Jo, Bloggs
        """,
        placeholders=['phone_number', 'First Name', 'lastname'],
        template_type='sms'
    )
    first_row = recipients[0]
    assert first_row.get(key).data == expected
    assert first_row[key].data == expected
    assert first_row.recipient == '07700900460'
    assert len(first_row.items()) == 3
    assert not recipients.has_errors

    assert recipients.missing_column_headers == set()
    recipients.placeholders = {'one', 'TWO', 'Thirty_Three'}
    assert recipients.missing_column_headers == {'one', 'TWO', 'Thirty_Three'}
    assert recipients.has_errors


def test_error_if_too_many_recipients():
    recipients = RecipientCSV(
        'phone number,\n07700900460,\n07700900460,\n07700900460,',
        placeholders=['phone_number'],
        template_type='sms',
        remaining_messages=2
    )
    assert recipients.has_errors
    assert recipients.more_rows_than_can_send


def test_dont_error_if_too_many_recipients_not_specified():
    recipients = RecipientCSV(
        'phone number,\n07700900460,\n07700900460,\n07700900460,',
        placeholders=['phone_number'],
        template_type='sms'
    )
    assert not recipients.has_errors
    assert not recipients.more_rows_than_can_send


@pytest.mark.parametrize('index, expected_row', [
    (
        0,
        {
            'phone number': '07700 90000 1',
            'colour': 'red',
        },
    ),
    (
        1,
        {
            'phone_number': '07700 90000 2',
            'COLOUR': 'green',
        },
    ),
    (
        2,
        {
            'p h o n e  n u m b e r': '07700 90000 3',
            '   colour   ': 'blue'
        },
    ),
    pytest.mark.xfail((
        3,
        {'phone number': 'foo'},
    ), raises=IndexError),
    (
        -1,
        {
            'p h o n e  n u m b e r': '07700 90000 3',
            '   colour   ': 'blue'
        },
    ),
])
def test_recipients_can_be_accessed_by_index(index, expected_row):
    recipients = RecipientCSV(
        """
            phone number, colour
            07700 90000 1, red
            07700 90000 2, green
            07700 90000 3, blue
        """,
        placeholders=['phone_number'],
        template_type='sms'
    )
    for key, value in expected_row.items():
        assert recipients[index][key].data == value


@pytest.mark.parametrize('international_sms', (True, False))
def test_multiple_sms_recipient_columns(international_sms):
    recipients = RecipientCSV(
        """
            phone number, phone number, phone_number, foo
            07900 900111, 07900 900222, 07900 900333, bar
        """,
        template_type='sms',
        international_sms=international_sms,
    )
    assert recipients.column_headers == ['phone number', 'phone_number', 'foo']
    assert recipients.column_headers_as_column_keys == dict(phonenumber='', foo='').keys()
    assert recipients.rows[0].get('phone number').data == (
        '07900 900333'
    )
    assert recipients.rows[0].get('phone_number').data == (
        '07900 900333'
    )
    assert recipients.rows[0].get('phone number').error is None
    assert recipients.duplicate_recipient_column_headers == OrderedSet([
        'phone number', 'phone_number'
    ])
    assert recipients.has_errors


def test_multiple_email_recipient_columns():
    recipients = RecipientCSV(
        """
            EMAILADDRESS, email_address, foo
            one@two.com,  two@three.com, bar
        """,
        template_type='email',
    )
    assert recipients.rows[0].get('email address').data == (
        'two@three.com'
    )
    assert recipients.rows[0].get('email address').error is None
    assert recipients.has_errors
    assert recipients.duplicate_recipient_column_headers == OrderedSet([
        'EMAILADDRESS', 'email_address'
    ])
    assert recipients.has_errors


def test_multiple_letter_recipient_columns():
    recipients = RecipientCSV(
        """
            address line 1, Address Line 2, address line 1, address_line_2
            1,2,3,4
        """,
        template_type='letter',
    )
    assert recipients.rows[0].get('addressline1').data == (
        '3'
    )
    assert recipients.rows[0].get('addressline1').error is None
    assert recipients.has_errors
    assert recipients.duplicate_recipient_column_headers == OrderedSet([
        'address line 1', 'Address Line 2', 'address line 1', 'address_line_2'
    ])
    assert recipients.has_errors
