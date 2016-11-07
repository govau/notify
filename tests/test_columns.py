from notifications_utils.columns import Columns


def test_columns_as_dict_with_keys():
    assert Columns({
        'Date of Birth': '01/01/2001',
        'TOWN': 'London'
    }).as_dict_with_keys({'date_of_birth', 'town'}) == {
        'date_of_birth': '01/01/2001',
        'town': 'London'
    }


def test_columns_as_dict():
    assert dict(Columns({
        'date of birth': '01/01/2001',
        'TOWN': 'London'
    })) == {
        'dateofbirth': '01/01/2001',
        'town': 'London'
    }
