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
