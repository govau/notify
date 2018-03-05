from functools import lru_cache


class Columns():

    def __init__(self, row_dict):
        self._dict = {
            Columns.make_key(key): value for key, value in row_dict.items()
        }

    @classmethod
    def from_keys(cls, keys):
        return cls({key: key for key in keys})

    def __getitem__(self, key):
        return self.get(key)

    def __dict__(self):
        return self._dict

    def get(self, key, default=None):
        return self._dict.get(Columns.make_key(key), default)

    def items(self):
        return self._dict.items()

    def pop(self, key):
        return self._dict.pop(key)

    def copy(self):
        return Columns(self._dict.copy())

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def as_dict_with_keys(self, keys):
        return {
            key: self.get(key) for key in keys
        }

    @staticmethod
    @lru_cache(maxsize=32, typed=False)
    def make_key(original_key):
        if original_key is None:
            return None
        return "".join(
            character.lower() for character in original_key if character not in ' _-'
        )


class Row(Columns):

    message_too_long = False

    def __init__(
        self,
        row_dict,
        index,
        error_fn,
        placeholders,
        template,
    ):

        self.index = index

        if template:
            template.values = row_dict
            self.message_too_long = template.is_message_too_long()

        super().__init__({
            key: Cell(key, value, error_fn, placeholders)
            for key, value in row_dict.items()
        })

    def get(self, key):
        return self._dict.get(Columns.make_key(key), Cell())


class Cell():

    def __init__(
        self,
        key=None,
        value=None,
        error_fn=None,
        placeholders=None
    ):
        self.data = value
        self.error = error_fn(key, value) if error_fn else None
        self.ignore = Columns.make_key(key) not in (placeholders or [])
