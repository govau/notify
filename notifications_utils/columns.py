class Columns():

    def __init__(self, row_dict):
        self._dict = {
            Columns.make_key(key): value for key, value in row_dict.items()
        }

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None):
        return self._dict.get(Columns.make_key(key), default)

    def items(self):
        return self._dict.items()

    def pop(self, key):
        return self._dict.pop(key)

    def copy(self):
        return Columns(self._dict.copy())

    @staticmethod
    def make_key(original_key):
        if original_key is None:
            return None
        return "".join(
            character.lower() for character in original_key if character not in ' _-'
        )
